# make_DRAL_release.py    October 25, 2022    Jonathan Avila
# This script creates a DRAL release. Its input is the metadata Excel workbook (.xlsx),
# conversation audios (.wav), and conversation markups (.eaf). Its output is the updated
# metadata (.csv), fragment audios (.wav), and a copy of the conversation audios (.wav).

from itertools import product
from pathlib import Path
import shutil

import pandas as pd
from tqdm.contrib.concurrent import process_map


import _elan_funcs
from _markup_funcs import MarkupTier
import _pandas_funcs
import _sox_funcs


def make_dirs_in_path(path: str) -> None:
    # Create any directories in `path` if they do not exist.
    path.mkdir(parents=True, exist_ok=True)


def timedelta_to_string(td: pd.Timedelta) -> str:
    # Convert `td` to a string with the format `m:s.ms`.
    td_str = ""
    if td is not pd.NaT:
        minutes = td.components.minutes
        seconds = td.components.seconds
        milliseconds = td.components.milliseconds
        td_str = f"{minutes}:{seconds}.{milliseconds:03}"
    return td_str


def main() -> None:

    parent_dir = Path(__file__).parent

    # Input paths. The recordings directory should contain the conversation audios
    # (.wav). The metadata should should be an Excel workbook (.xlsx) with sheets
    # "conversation", "participant", and "producer". The DRAL technical report describes
    # the fields in each sheet.
    input_recordings_dir = parent_dir.joinpath("recordings")
    input_metadata_path = parent_dir.joinpath("metadata.xlsx")

    # Output paths.
    release_dir = parent_dir.joinpath("release")
    conv_dir = release_dir.joinpath("recordings")
    short_frag_dir = release_dir.joinpath("fragments-short")
    long_frag_dir = release_dir.joinpath("fragments-long")
    concat_frag_dir = release_dir.joinpath("fragments-short-concatenated")

    # Expected values.
    exp_lang_codes = ["EN", "ES", "JA"]
    exp_conv_id_pattern = (
        rf"(?P<lang_code>{'|'.join(exp_lang_codes)})_(?P<conv_num>\d{{{3}}})"
    )
    exp_og_conv_code = "OG"
    exp_re_conv_code = "RE"
    exp_tier_left = MarkupTier("LittleLeft", "l", {1: [1]})
    exp_tier_right = MarkupTier("LittleRight", "r", {1: [2]})
    exp_tier_both = MarkupTier("Utterance")
    exp_tier_name_pattern = "|".join(MarkupTier.all_tiers.keys())
    exp_markup_val_pattern = r"^#?\d+$"

    # Make all directories in output paths.
    make_dirs_in_path(release_dir)
    make_dirs_in_path(conv_dir)
    make_dirs_in_path(short_frag_dir)
    make_dirs_in_path(long_frag_dir)
    make_dirs_in_path(concat_frag_dir)

    # Check whether the metadata file exists.
    if not input_metadata_path.is_file():
        print(f"File does not exist: {input_metadata_path}")
        return

    # Read original metadata sheets into pandas DataFrames.
    df_participant = pd.read_excel(input_metadata_path, "participant")
    df_producer = pd.read_excel(input_metadata_path, "producer")
    df_conv = pd.read_excel(input_metadata_path, "conversation")

    print("Reading conversations...")

    # Add columns to conversation DataFrame: language code, conversation number. The
    # language code conversation number makes up the conversation ID.
    id_match_groups = df_conv["id"].str.extractall(exp_conv_id_pattern)
    df_conv["lang_code"] = id_match_groups.lang_code.values
    df_conv["conv_num"] = id_match_groups.conv_num.values

    # Add column to conversation DataFrame: expected audio path.
    df_conv["audio_path"] = df_conv["id"].apply(
        lambda id: input_recordings_dir.joinpath(id + ".wav")
    )

    # Add column to conversation DataFrame: expected markup path.
    df_conv["markup_path"] = df_conv.loc[:, "id"].apply(
        lambda id: input_recordings_dir.joinpath(id + ".eaf")
    )

    # Add column to conversation DataFrame: copy audio path (the path the copy of its
    # audio will be written to).
    df_conv["copy_audio_path"] = df_conv.loc[:, "id"].apply(
        lambda id: conv_dir.joinpath(f"{id}.wav")
    )

    # Remove conversations with unexpected ID.
    df_conv = _pandas_funcs.remove_not_in_pattern(df_conv, "id", exp_conv_id_pattern)

    # Remove conversations with unexpected original or re-enacted code.
    df_conv = _pandas_funcs.remove_not_in_list(
        df_conv, "original_or_reenacted", [exp_og_conv_code, exp_re_conv_code]
    )

    # Remove conversations with missing audio.
    df_conv = _pandas_funcs.remove_file_not_found(df_conv, "audio_path")

    # Remove conversations with missing markup.
    df_conv = _pandas_funcs.remove_file_not_found(df_conv, "markup_path")

    def get_conv_trans_id(df_conv_row: pd.DataFrame) -> str:
        # Returns the inferred conversation ID of a conversation's translation, or None
        # if it could not be inferred. A conversation should have exactly one
        # translation with the same conversation number, a different language code, and
        # a different original or re-enacted code.
        trans_id = None
        has_same_conv_num = df_conv["conv_num"] == df_conv_row.conv_num
        has_diff_lang_code = df_conv["lang_code"] != df_conv_row.lang_code
        has_diff_og_re_code = (
            df_conv["original_or_reenacted"] != df_conv_row.original_or_reenacted
        )
        df_trans = df_conv[has_same_conv_num & has_diff_lang_code & has_diff_og_re_code]
        n_translations = df_trans.shape[0]
        if n_translations == 1:
            trans_row = df_trans.iloc[0]
            trans_id = trans_row.id
        return trans_id

    # Add column to conversation DataFrame: translation ID.
    df_conv["trans_id"] = df_conv.apply(get_conv_trans_id, axis=1)

    # Remove conversations without translations.
    df_conv = _pandas_funcs.remove_missing(df_conv, "trans_id")

    print("Reading markups...")

    # Read all markups into a single DataFrame. Add columns to markup DataFrame: source
    # conversation ID, source conversation translation ID, conversation audio path,
    # original or re-enecated code. Note: Appending to a list before converting to a
    # DataFrame is faster than appending to a DataFrame.
    df_markup_to_concat = []
    for conv in df_conv.itertuples():
        df_conv_markup = _elan_funcs.read_eaf_into_df(conv.markup_path)
        df_conv_markup["conv_id"] = conv.id
        df_conv_markup["trans_conv_id"] = conv.trans_id
        df_conv_markup["conv_lang_code"] = conv.lang_code
        df_conv_markup["conv_audio_path"] = conv.audio_path
        df_conv_markup["original_or_reenacted"] = conv.original_or_reenacted
        df_markup_to_concat.append(df_conv_markup)
    df_markup = pd.concat(df_markup_to_concat)

    # Write conversation audio copies (parallel).
    print("Writing conversation audios...")
    process_map(
        shutil.copy,
        df_conv["audio_path"],
        df_conv["copy_audio_path"],
        total=len(df_conv),
    )

    # Convert markup DataFrame duration columns from milliseconds (float) to duration
    # (pandas Timedelta).
    df_markup["time_start"] = pd.to_timedelta(df_markup["time_start"], "ms")
    df_markup["time_end"] = pd.to_timedelta(df_markup["time_end"], "ms")

    # Add column to markup DataFrame: markup ID. A markup ID is made up of the source
    # conversation ID and the markup value.
    df_markup["id"] = df_markup["conv_id"] + "_" + df_markup["value"]

    # Add column to markup DataFrame: translation markup ID.
    df_markup["trans_id"] = df_markup["trans_conv_id"] + "_" + df_markup["value"]

    # Add column to markup DataFrame: sox remix dictionary (to use when extracting
    # fragment audios later).
    df_markup["remix_dict"] = df_markup["tier_name"].apply(
        lambda tier_name: MarkupTier.all_tiers[tier_name].remix_dict
    )

    # Add column to markup DataFrame: duration.
    df_markup["duration"] = df_markup["time_end"] - df_markup["time_start"]

    # Remove markups with unexpected tier.
    df_markup = _pandas_funcs.remove_not_in_pattern(
        df_markup, "tier_name", exp_tier_name_pattern
    )

    # Remove markups with unexpected value.
    df_markup = _pandas_funcs.remove_not_in_pattern(
        df_markup, "value", exp_markup_val_pattern
    )

    # Remove markups with duplicate values.
    df_markup = _pandas_funcs.remove_duplicates(
        df_markup, ["conv_id", "tier_name", "value"]
    )

    # Remove markups without translation.
    df_markup = _pandas_funcs.remove_not_shared_in_col(df_markup, "trans_id", "id")

    # Store the indices of markups belonging to short fragments and long fragments.
    is_short_frag = df_markup["tier_name"].isin(
        [exp_tier_left.name, exp_tier_right.name]
    )
    is_long_frag = df_markup["tier_name"] == exp_tier_both.name

    # Add column to markup DataFrame: fragment audio path (the path its audio will be
    # written to).
    df_markup.loc[is_short_frag, "audio_path"] = df_markup.loc[
        is_short_frag, "id"
    ].apply(lambda id: short_frag_dir.joinpath(f"{id}.wav"))
    df_markup.loc[is_long_frag, "audio_path"] = df_markup.loc[is_long_frag, "id"].apply(
        lambda id: long_frag_dir.joinpath(f"{id}.wav")
    )

    # Write short fragment audios (parallel).
    print("Writing fragment audios...")
    process_map(
        _sox_funcs.build_audio,
        df_markup["time_start"],
        df_markup["time_end"],
        df_markup["conv_audio_path"],
        df_markup["audio_path"],
        df_markup["remix_dict"],
        total=len(df_markup),
    )

    print("Setting up concatenated short fragments audios...")

    # Create a list of fragments to concatenate. Each item in the list is a tuple of a
    # list of input fragment audio paths and an output concatenated audio path.
    frags_to_concat = []
    unique_conv_ids = df_markup["conv_id"].unique()
    short_tiers = [exp_tier_left, exp_tier_right]
    for conv_id, tier in list(product(unique_conv_ids, short_tiers)):
        in_cov = df_markup["conv_id"] == conv_id
        in_tier = df_markup["tier_name"] == tier.name
        in_track = in_cov & in_tier

        # Ignore tracks without fragments to concatenate.
        if ~in_track.any():
            continue

        concat_audio_path = concat_frag_dir.joinpath(f"{conv_id}{tier.short_name}.wav")

        # Append input audio paths and output audio path tuple to list.
        frag_audio_paths = list(df_markup.loc[in_track, "audio_path"])
        frags_to_concat.append((frag_audio_paths, concat_audio_path))

        # Add columns to markup DataFrame: concatenated audio relative start time,
        # concatenated audio relative end time.
        first_duration = df_markup.loc[in_track, "duration"].iloc[0]
        df_markup.loc[in_track, "time_end_rel"] = df_markup.loc[
            in_track, "duration"
        ].cumsum()
        df_markup.loc[in_track, "time_start_rel"] = (
            df_markup.loc[in_track, "time_end_rel"] - first_duration
        )

        # Add column markup DataFrame: concatenated audio path (the path the
        # concatenated audio will be written to).
        df_markup.loc[in_track, "concat_audio_path"] = concat_audio_path

    # Write concatenated short fragment audios (parallel).
    print("Writing concatenated short fragment audios...")
    process_map(
        _sox_funcs.concat_audios,
        list(zip(*frags_to_concat))[0],  # input fragment audio paths
        list(zip(*frags_to_concat))[1],  # output concatenated audio paths
        total=len(frags_to_concat),
    )

    # Convert duration columns to strings.
    df_markup["time_start"] = df_markup["time_start"].apply(timedelta_to_string)
    df_markup["time_end"] = df_markup["time_end"].apply(timedelta_to_string)
    df_markup["time_start_rel"] = df_markup["time_start_rel"].apply(timedelta_to_string)
    df_markup["time_end_rel"] = df_markup["time_end_rel"].apply(timedelta_to_string)
    df_markup["duration"] = df_markup["duration"].apply(timedelta_to_string)

    print("Writing CSVs...")

    # Write participant metadata to CSV.
    df_participant.to_csv(release_dir.joinpath("participant.csv"), index=False)

    # Write producer metadata to CSV.
    df_producer.to_csv(release_dir.joinpath("producer.csv"), index=False)

    # Write conversation metadata to CSV. The column for notes is excluded because it
    # contains internal notes.
    df_conv.to_csv(
        release_dir.joinpath("conversation.csv"),
        index=False,
        columns=[
            "id",
            "date",
            "original_or_reenacted",
            "participant_id_left",
            "participant_id_right",
            "producer_id",
            "trans_id",
        ],
    )

    # Write short fragments, long fragments, and concatenated short fragments metadata
    # to CSVs. The markup DataFrame combines all of these, so only some rows and columns
    # are selected for each.
    df_markup[is_short_frag].to_csv(
        release_dir.joinpath("fragments_short.csv"),
        index=False,
        columns=[
            "id",
            "conv_id",
            "original_or_reenacted",
            "time_start",
            "time_end",
            "duration",
            "trans_id",
        ],
    )
    df_markup[is_long_frag].to_csv(
        release_dir.joinpath("fragments_long.csv"),
        index=False,
        columns=[
            "id",
            "conv_id",
            "original_or_reenacted",
            "time_start",
            "time_end",
            "duration",
            "trans_id",
        ],
    )
    df_markup[is_short_frag].to_csv(
        release_dir.joinpath("fragments_short_concatenated.csv"),
        index=False,
        columns=["id", "time_start_rel", "time_end_rel", "duration", "trans_id"],
    )


if __name__ == "__main__":
    main()
