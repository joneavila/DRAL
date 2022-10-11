# make_DRAL_release.py    October 11, 2022    Jonathan Avila

import collections
from pathlib import Path
import re
import shutil

import pandas as pd
from pympi import Eaf
from sox import Combiner, Transformer


def make_dirs_in_path(path: str) -> None:
    # Create any directories in a path if they do not exist.
    path.mkdir(parents=True, exist_ok=True)


def timedelta_to_string(td: pd.Timedelta) -> str:
    # Convert a pandas Timedelta to a string with the format `m:s.ms`.
    minutes = td.components.minutes
    seconds = td.components.seconds
    milliseconds = td.components.milliseconds
    return f"{minutes}:{seconds}.{milliseconds:03}"


def read_eaf_into_df(eaf_path: Path) -> pd.DataFrame:
    # Read all tier annotation data in an Elan file into a pandas DataFrame with the
    # columns: value, tier_name, time_start, time_end, duration.

    eaf = Eaf(eaf_path)
    markup = []
    for tier_name, tier_data in eaf.tiers.items():
        aligned_annotations, _, _, _ = tier_data
        for annotation in aligned_annotations.values():
            ts_start, ts_end, value, _ = annotation
            time_start = eaf.timeslots[ts_start]
            time_end = eaf.timeslots[ts_end]
            markup.append((value, tier_name, time_start, time_end))
    df_markup = pd.DataFrame(
        markup, columns=["value", "tier_name", "time_start", "time_end"]
    )

    # Convert durations from milliseconds (float) to duration (pandas Timedelta).
    df_markup["time_start"] = pd.to_timedelta(df_markup["time_start"], "ms")
    df_markup["time_end"] = pd.to_timedelta(df_markup["time_end"], "ms")

    # Add a duration column.
    df_markup["duration"] = df_markup["time_end"] - df_markup["time_start"]

    return df_markup


def read_dral_eaf_into_df(eaf_path: Path, trans_eaf_path: Path) -> pd.DataFrame:
    # Read all markup data in Elan file at `eaf_path` into a pandas DataFrame with the
    # columns: value, tier_name, time_start, time_end, duration, frag_type, channel_num.
    # Remove markups with an unexpected value, in an unexpected tier, with duplicate
    # values in the same tier, or not found in the same tier in the translation.

    def is_translated(markup_row: pd.DataFrame, df_trans_markup: pd.DataFrame) -> bool:
        in_same_tier = df_trans_markup["tier_name"] == markup_row.tier_name
        has_same_value = df_trans_markup["value"] == markup_row.value
        translations_df = df_trans_markup[in_same_tier & has_same_value]
        n_translations = translations_df.shape[0]
        return n_translations == 1

    df_markup = read_eaf_into_df(eaf_path)
    df_trans_markup = read_eaf_into_df(trans_eaf_path)

    Tier = collections.namedtuple("Tier", ["frag_type", "channel_num"])
    valid_tiers = {
        "LittleLeft": Tier("short", 1),
        "LittleRight": Tier("short", 2),
        "Utterance": Tier("long", [1, 2]),
    }

    # Remove markups in unexpected tiers.
    valid_tier_names = list(valid_tiers.keys())
    tier_pattern = re.compile(rf"({'|'.join(valid_tier_names)})")
    is_valid_tier = df_markup["tier_name"].str.fullmatch(tier_pattern).notnull()
    if ~is_valid_tier.all():
        print(
            eaf_path.name,
            "\tThese markups are in an unexpected tier and will be ignored: ",
            list(df_markup[~is_valid_tier]["tier_name", "value"]),
        )
        df_markup = df_markup[is_valid_tier]

    # Remove markups in the same tier with duplicate values.
    is_duplicate = df_markup.duplicated(["tier_name", "value"], False)
    if is_duplicate.any():
        print(
            eaf_path.name,
            "\tThese markups have duplicate values and will be ignored: ",
            list(df_markup[is_duplicate]["tier_name", "value"]),
        )
        df_markup = df_markup[~is_duplicate]

    # Remove markups that do not follow the pattern: pound symbol (optional), digits.
    val_pattern = re.compile(r"^#?\d+$")
    is_valid_value = df_markup["value"].str.fullmatch(val_pattern).notnull()
    if ~is_valid_value.all():
        print(
            eaf_path.name,
            "\tThese markups have unexpected values and will be ignored: ",
            list(df_markup[~is_valid_value]["tier_name", "value"]),
        )
        df_markup = df_markup[is_valid_value]

    # Remove markups that are not found in the translation.
    has_translation = df_markup.apply(
        is_translated, df_trans_markup=df_trans_markup, axis=1
    )
    if ~has_translation.all():
        print(
            eaf_path.name,
            "\tThese markups have zero or more than one translation and will be "
            "ignored: ",
            list(df_markup[~has_translation][["tier_name", "value"]].values.tolist()),
        )
        df_markup = df_markup[~has_translation]

    # Add a column for fragment type.
    df_markup["frag_type"] = df_markup["tier_name"].apply(
        lambda name: valid_tiers[name].frag_type
    )

    # Add a column for channel number.
    df_markup["channel_num"] = df_markup["tier_name"].apply(
        lambda name: valid_tiers[name].channel_num
    )

    return df_markup


def clean_up_conv_df(df_conv: pd.DataFrame, recordings_dir: Path):
    # Remove conversations with: an unexpected ID, an unexpected original or re-enacted
    # code, has missing audio, has missing markup, or has zero or more than one
    # translations.

    def get_conv_trans_ID(conv_row: pd.DataFrame) -> str:
        # Return the ID of the conversation's translation or None if it does not have a
        # translation or more than one translation.

        trans_id = None

        id = conv_row.id
        lang_code = conv_row.lang_code
        og_re_code = conv_row.original_or_reenacted

        # Translations should have an ID similar to the current conversation but with a
        # different language code and should have an original or re-enacted code
        # opposite to the current conversation.
        (val_trans_lang_codes := valid_lang_codes.copy()).remove(lang_code)
        val_trans_ids = [id.replace(lang_code, code) for code in val_trans_lang_codes]
        val_trans_ids_pattern = "|".join(val_trans_ids)
        has_valid_trans_id = df_conv["id"].str.contains(val_trans_ids_pattern)
        has_valid_og_re_code = df_conv["original_or_reenacted"] != og_re_code
        df_translations = df_conv[has_valid_trans_id & has_valid_og_re_code]

        n_translations = df_translations.shape[0]
        if n_translations == 1:
            trans_row = df_translations.iloc[0]
            trans_id = trans_row.id
        return trans_id

    valid_lang_codes = ["EN", "ES", "JP"]

    # ID should follow the format: valid language code, underscore, three digits.
    id_pattern = re.compile(rf"(?P<lang_code>{'|'.join(valid_lang_codes)})_(\d{{{3}}})")

    og_conv_code = "OG"
    re_conv_code = "RE"
    og_re_code_pattern = re.compile(rf"({og_conv_code}|{re_conv_code})")

    # Remove conversations with unexpected ID.
    is_valid_id = df_conv["id"].str.fullmatch(id_pattern)
    if ~is_valid_id.all():
        print(
            "These conversations have an unexpected ID and will be ignored :",
            list(df_conv[~is_valid_id]["id"]),
        )
        df_conv = df_conv[is_valid_id]

    # Copy the language code to a new column.
    id_match_groups = df_conv["id"].str.extractall(id_pattern)
    df_conv["lang_code"] = id_match_groups.lang_code.values

    # Remove conversations with unexpected original or re-enacted code.
    is_valid_code = df_conv["original_or_reenacted"].str.fullmatch(og_re_code_pattern)
    if ~is_valid_code.all():
        print(
            "These conversations have an unexpected original or re-enacted code and "
            "will be ignored:",
            list(df_conv[~is_valid_code]["id"]),
        )
        df_conv = df_conv[is_valid_code]

    # Add a column for the expected audio path.
    df_conv["audio_path"] = df_conv["id"].apply(
        lambda id: recordings_dir.joinpath(id + ".wav")
    )

    # Remove conversations with missing audio.
    has_audio = df_conv["audio_path"].apply(lambda path: path.exists())
    if ~has_audio.all():
        print(
            "These conversations are missing audio and will be ignored: ",
            list(df_conv[~has_audio]["id"]),
        )
        df_conv = df_conv[has_audio]

    # Add a column for the expected markup path.
    df_conv["markup_path"] = df_conv["id"].apply(
        lambda id: recordings_dir.joinpath(id + ".eaf")
    )

    # Remove conversations with missing markup.
    has_markup = df_conv["markup_path"].apply(lambda path: path.exists())
    if ~has_markup.all():
        print(
            "These conversations are missing markup and will be ignored: ",
            list(df_conv[~has_markup]["id"]),
        )
        df_conv = df_conv[has_markup]

    # Add a column for the translation ID.
    df_conv["trans_id"] = df_conv.apply(get_conv_trans_ID, axis=1)

    # Remove conversations without translations.
    has_translation = df_conv["trans_id"].notnull()
    if ~has_translation.all():
        print(
            "These conversations do not have a translation with a valid ID and "
            "original and re-enacted code or have multiple translations and will be "
            "ignored:",
            list(df_conv[~has_translation]["id"]),
        )
    df_conv = df_conv[has_translation]

    df_conv.set_index("id", inplace=True, drop=False)
    return df_conv


def main():

    parent_dir = Path(__file__).parent

    input_recordings_dir = parent_dir.joinpath("recordings")
    input_metadata_path = parent_dir.joinpath("metadata.xlsx")

    release_dir = parent_dir.joinpath("release")
    conv_dir = release_dir.joinpath("recordings")
    short_frag_dir = release_dir.joinpath("fragments-short")
    long_frag_dir = release_dir.joinpath("fragments-long")
    concat_dir = release_dir.joinpath("fragments-short-concatenated")

    make_dirs_in_path(release_dir)
    make_dirs_in_path(conv_dir)
    make_dirs_in_path(short_frag_dir)
    make_dirs_in_path(long_frag_dir)
    make_dirs_in_path(concat_dir)

    transformer = Transformer()
    combiner = Combiner()

    df_participant = pd.read_excel(input_metadata_path, "participant")
    df_producer = pd.read_excel(input_metadata_path, "producer")

    df_conv_original = pd.read_excel(input_metadata_path, "conversation")
    df_conv = clean_up_conv_df(df_conv_original, input_recordings_dir)

    # Copy conversation audios to the release.
    for conv in df_conv.itertuples():
        audio_copy_path = conv_dir.joinpath(f"{conv.id}.wav")
        shutil.copy(conv.audio_path, audio_copy_path)

    # Read all markup into a single DataFrame. Add columns for source conversation ID,
    # markup ID, translation markup ID, and source conversation audio path.
    print("Reading markups...")
    df_markup_to_concat = []
    for conv in df_conv.itertuples():
        trans_row = df_conv.loc[conv.trans_id]
        df_conv_markup = read_dral_eaf_into_df(conv.markup_path, trans_row.markup_path)
        df_conv_markup["conv_id"] = conv.id
        df_conv_markup["id"] = df_conv_markup["conv_id"] + "_" + df_conv_markup["value"]
        df_conv_markup["trans_id"] = df_conv_markup["id"].apply(
            lambda id: id.replace(conv.lang_code, trans_row.lang_code)
        )
        df_conv_markup["conv_audio_path"] = conv.audio_path
        df_conv_markup["original_or_reenacted"] = conv.original_or_reenacted
        df_markup_to_concat.append(df_conv_markup)
    df_markup = pd.concat(df_markup_to_concat)

    is_short_frag = df_markup["frag_type"] == "short"
    is_long_frag = df_markup["frag_type"] == "long"

    df_markup.loc[is_short_frag, "audio_path"] = df_markup.loc[
        is_short_frag, "id"
    ].apply(lambda id: short_frag_dir.joinpath(f"{id}.wav"))

    df_markup.loc[is_long_frag, "audio_path"] = df_markup.loc[is_long_frag, "id"].apply(
        lambda id: long_frag_dir.joinpath(f"{id}.wav")
    )

    # Write short fragment audios. Trim the audio to just the fragment and mix the
    # relevant channel down to one channel.
    print("Writing short fragment audios...")
    for frag in df_markup[is_short_frag].itertuples():
        print("\t", frag.id)
        transformer.remix({1: [frag.channel_num]})
        transformer.trim(frag.time_start.total_seconds(), frag.time_end.total_seconds())
        transformer.build_file(str(frag.conv_audio_path), str(frag.audio_path))
        transformer.clear_effects()

    # Write long fragment audios. Trim the audio to just the fragment.
    print("Writing long fragments audios...")
    for frag in df_markup[is_long_frag].itertuples():
        print("\t", frag.id)
        transformer.trim(frag.time_start.total_seconds(), frag.time_end.total_seconds())
        transformer.build_file(str(frag.conv_audio_path), str(frag.audio_path))
        transformer.clear_effects()

    # Concatenate short fragments for each conversation.
    print("Writing concatenated short fragments audios...")
    for conv in df_conv.itertuples():

        print(f"\t{conv.id}")
        in_conv = df_markup["conv_id"] == conv.id

        # For each track.
        for channel_num, track_code in zip([1, 2], ["l", "r"]):

            in_channel = df_markup["channel_num"] == channel_num

            # in_track_index = df_markup[in_conv & in_channel].index
            in_track = in_conv & in_channel & is_short_frag

            # Concatenate all short fragments in this track. Downsample to 16 kHz.
            frag_audio_paths = list(df_markup.loc[in_track, "audio_path"])
            frag_audio_paths_str = [str(path) for path in frag_audio_paths]
            concat_audio_path = concat_dir.joinpath(f"{conv.id}{track_code}.wav")
            combiner.input_format = None
            combiner.convert(16000)
            combiner.build(frag_audio_paths_str, str(concat_audio_path), "concatenate")
            combiner.clear_effects()

            # Add columns for relative start and end time in concatenated audio.
            first_duration = df_markup.loc[in_track, "duration"].iloc[0]
            df_markup.loc[in_track, "time_end_rel"] = df_markup.loc[
                in_track, "duration"
            ].cumsum()
            df_markup.loc[in_track, "time_start_rel"] = (
                df_markup.loc[in_track, "time_end_rel"] - first_duration
            )

    # Convert duration columns to strings.
    df_markup["time_start"] = df_markup["time_start"].apply(timedelta_to_string)
    df_markup["time_end"] = df_markup["time_end"].apply(timedelta_to_string)
    df_markup.loc[is_short_frag, "time_start_rel"] = df_markup.loc[
        is_short_frag, "time_start_rel"
    ].apply(timedelta_to_string)
    df_markup.loc[is_short_frag, "time_end_rel"] = df_markup.loc[
        is_short_frag, "time_end_rel"
    ].apply(timedelta_to_string)
    df_markup["duration"] = df_markup["duration"].apply(timedelta_to_string)

    # Write the updated metadata as CSV files.
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
    df_participant.to_csv(release_dir.joinpath("participant.csv"), index=False)
    df_producer.to_csv(release_dir.joinpath("producer.csv"), index=False)
    df_markup[is_short_frag].to_csv(
        release_dir.joinpath("fragments_short.csv"),
        index=False,
        columns=[
            "id",
            "original_or_reenacted",
            "time_start",
            "time_end",
            "duration",
            "conv_id",
            "trans_id",
        ],
    )
    df_markup[is_long_frag].to_csv(
        release_dir.joinpath("fragments_long.csv"),
        index=False,
        columns=[
            "id",
            "original_or_reenacted",
            "time_start",
            "time_end",
            "duration",
            "conv_id",
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
