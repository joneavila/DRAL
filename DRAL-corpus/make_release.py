# This script makes a DRAL release. See help message below.
import argparse
from pathlib import Path
from shutil import copy
from typing import Tuple

import pandas as pd
import shared
from tqdm.contrib.concurrent import process_map
from utils.dirs import make_dirs_in_path_if_not_exist
from utils.elan import elan_to_dataframe
from utils.sox import is_silent, trim_remix_audio, validate_with_sox


def main() -> None:

    # TODO Set index for remaining DataFrames and write to CSV.

    dir_this_file = Path(__file__).parent.resolve()

    parser = argparse.ArgumentParser(
        description="Make a Dialogs Re-enacted Across Languages (DRAL) release.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--dir_input",
        help="Directory containing a conversations metadata file (.xlsx) and a "
        "subdirectory named 'recordings' containing their audios (.wav) and markups "
        "(.eaf). For more information on the metadata Excel workbook sheets and "
        "fields, see the techincal report.",
        default=dir_this_file.joinpath("raw-data"),
    )
    parser.add_argument(
        "-o",
        "--dir_output",
        help="Directory to write release contents: copies of the conversation audios "
        "(.wav), conversation short fragment audios (.wav), conversation long fragment "
        "audios (.wav), and the following metadata sheets (.csv): conversation, "
        "fragments-short, fragments-long, participant, producer.",
        default=dir_this_file.joinpath("release"),
    )
    parser.add_argument(
        "--warn-silence",
        help="Print IDs of short conversation fragments that are mostly silent.",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--overwrite",
        help="Overwrite contents in the output directory (ignore warning).",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    args = parser.parse_args()

    NAME_DIR_RECORDINGS = "recordings"
    NAME_FILE_METADATA = "metadata.xlsx"

    dir_input = Path(args.dir_input)
    dir_input_recordings = dir_input.joinpath(NAME_DIR_RECORDINGS)
    path_input_metadata = dir_input.joinpath(NAME_FILE_METADATA)

    dir_output_root = Path(
        args.dir_output
    )  # The output root directory will contain all output files.
    ignore_overwrite = args.overwrite

    if not dir_input_recordings.exists():
        print(
            f"Stopped. The specified input directory does not contain the audio "
            f"directory: {NAME_DIR_RECORDINGS}"
        )
        return
    if not path_input_metadata.exists():
        print(
            f"Stopped. The specified input directory does not contain the metadata "
            f"file: {NAME_FILE_METADATA}"
        )
        return

    if not dir_output_root.exists():
        make_dirs_in_path_if_not_exist(dir_output_root)

    dir_output_root_not_empty = any(dir_output_root.iterdir())
    if dir_output_root_not_empty and ignore_overwrite is False:
        print(
            "Stopped. The specified output directory is not empty. To ignore this "
            "check, see help message."
        )
        return

    # Check for broken audios with SoX, to avoid SoX errors downstream.
    print("Validating WAV files...")
    path_wav_list = list(dir_input_recordings.glob("*.wav"))
    wav_is_valid_list = process_map(
        validate_with_sox,
        path_wav_list,
        total=len(path_wav_list),
    )
    path_wav_invalid_list = [
        path_wav_list[wav_file_idx]
        for wav_file_idx, is_valid in enumerate(wav_is_valid_list)
        if is_valid is False
    ]
    if path_wav_invalid_list:
        print(
            "Stopping. These WAV files could not be read by SoX and are likely broken:"
        )
        for path_wav_invalid in path_wav_invalid_list:
            print(f"\t{str(path_wav_invalid)}")
        return

    print("Reading conversations...")
    dir_output_conv_audio = dir_output_root.joinpath("recordings")
    make_dirs_in_path_if_not_exist(dir_output_conv_audio)
    df_conv = _get_conversation_dataframe(
        path_input_metadata,
        dir_input_recordings,
        dir_output_conv_audio,
    )

    print("Reading markups...")
    dir_output_frag_audio_short = dir_output_root.joinpath("fragments-short")
    dir_output_frag_audio_long = dir_output_root.joinpath("fragments-long")
    make_dirs_in_path_if_not_exist(dir_output_frag_audio_short)
    make_dirs_in_path_if_not_exist(dir_output_frag_audio_long)
    df_markup_short, df_markup_long = _get_markup_dataframes(
        df_conv, dir_output_frag_audio_short, dir_output_frag_audio_long
    )

    print("Reading participants...")
    df_participant = _get_participant_dataframe(path_input_metadata, df_conv)

    print("Reading producers...")
    df_producer = _get_producer_dataframe(path_input_metadata, df_conv)

    # Write conversation audio copies in parallel.
    print("Writing conversation audios...")
    process_map(
        copy,
        df_conv["audio_path"],
        df_conv["copy_audio_path"],
        total=len(df_conv),
    )

    # If writing audios errors, it might be a corrupted audio file. I learned this the
    # hard way. The SoX library does not have a utility function for this so I have no
    # check unfortunately.
    # Write short fragment audios.
    print("Writing short fragment audios...")
    process_map(
        trim_remix_audio,
        df_markup_short["time_start"],
        df_markup_short["time_end"],
        df_markup_short["conv_audio_path"],
        df_markup_short["audio_path"],
        df_markup_short["remix_dict"],
        total=len(df_markup_short),
        chunksize=8,
    )

    # Warn about short fragments that may be silent.
    # TODO Replace with function in script print_silent_fragments.py
    if args.warn_silence:
        print("Detecting silent short fragments...")
        is_silent_frag = process_map(
            is_silent,
            df_markup_short["audio_path"],
            total=len(df_markup_short),
            # chunksize=8,
        )
        if any(is_silent_frag):
            print("These fragments may be silent:")
            print(df_markup_short[is_silent_frag].index)

    print("Writing long fragment audios...")
    process_map(
        trim_remix_audio,
        df_markup_long["time_start"],
        df_markup_long["time_end"],
        df_markup_long["conv_audio_path"],
        df_markup_long["audio_path"],
        total=len(df_markup_long),
        chunksize=8,
    )

    print("Writing CSVs...")

    # Write participant metadata to CSV.
    df_participant.to_csv(
        dir_output_root.joinpath("participant.csv"),
        index=False,
        columns=[
            "id",
            "id_unique",
            "lang1",
            "lang2",
            "lang_strength",
            "dialect_note1",
            "dialect_note2",
            "is_producer",
        ],
    )

    # Write producer metadata to CSV.
    df_producer.to_csv(
        dir_output_root.joinpath("producer.csv"), index=False, columns=["id"]
    )

    # Write conversation metadata to CSV.
    df_conv.to_csv(
        dir_output_root.joinpath("conversation.csv"),
        index=False,
        columns=[
            "id",
            "recording_date",
            "original_or_reenacted",
            "participant_id_left",
            "participant_id_right",
            "participant_id_left_unique",
            "participant_id_right_unique",
            "producer_id",
            "trans_id",
        ],
    )

    # Write short fragments metadata to CSVs.
    df_markup_short.to_csv(
        dir_output_root.joinpath("fragments-short.csv"),
        columns=[
            "participant_id",
            "participant_id_unique",
            "lang_code",
            "conv_id",
            "original_or_reenacted",
            "time_start",
            "time_end",
            "duration",
            "trans_id",
        ],
    )

    # Write short fragments metadata to a second CSV. This CSV includes all columns and
    # should excluded from public releases.
    df_markup_short.to_csv(
        dir_output_root.joinpath("fragments-short-complete.csv"),
    )

    # Write long fragments metadata to CSVs.
    df_markup_long.to_csv(
        dir_output_root.joinpath("fragments-long.csv"),
        columns=[
            "participant_id_left",
            "participant_id_right",
            "participant_id_left_unique",
            "participant_id_right_unique",
            "lang_code",
            "conv_id",
            "original_or_reenacted",
            "time_start",
            "time_end",
            "duration",
            "trans_id",
        ],
    )

    # Write long fragments metadata to a second CSV. This CSV includes all columns and
    # is excluded from public releases, used for my dissertation project.
    df_markup_long.to_csv(
        dir_output_root.joinpath("fragments-long-complete.csv"),
        index=False,
    )

    print(f"Done. Output written to: {dir_output_root}")


def _get_conversation_dataframe(
    path_input_metadata: Path,
    dir_input_recordings: Path,
    dir_output_conv_audio: Path,
) -> pd.DataFrame:

    # Read the original conversation metadata into a DataFrame.
    df_conv = pd.read_excel(path_input_metadata, "conversation")

    # Drop rows that contain NaN values. For each row to drop, print the column names
    # that contain NaN.
    df_conv_nan = df_conv[df_conv.isna().any(axis=1)]
    if df_conv_nan.shape[0] > 0:
        print(
            "The following conversation metadata rows were ignored because they contain NaN values:"
        )
        conv_metadata_row_start = 2
        for index, row in df_conv_nan.iterrows():
            index_adjusted = index + conv_metadata_row_start
            col_names_with_na = [name for name in row[row.isna()].index]
            print(f"\tRow {index_adjusted}: {col_names_with_na}")
        df_conv = df_conv.dropna(how="any")

    # The expected conversation ID pattern is: two alphabetical characters (language
    # code), followed by an underscore, followed by three digits (conversation number).
    # The language code capture group and conversation number capture group are both
    # named to help pull their values later.
    conv_id_re_pattern = (
        rf"(?P<lang_code>{'|'.join(shared.LANG_CODES)})_(?P<conv_num>\d{{{3}}})"
    )

    # Remove conversations with unexpected ID.
    has_expected_id = df_conv["id"].str.fullmatch(conv_id_re_pattern)
    if ~has_expected_id.all():
        print("These conversations were ignored because they have an unexpected ID:")
        print(df_conv.loc[~has_expected_id, ["id"]])
        df_conv = df_conv[has_expected_id]

    # Remove conversations with unexpected original or re-enacted code.
    has_expected_og_re_code = df_conv["original_or_reenacted"].isin(
        [shared.CONV_CODE_ORIGINAL, shared.CONV_CODE_REENACTED]
    )
    if ~has_expected_og_re_code.all():
        print(
            "These conversations were ignored because they have an unexpected original \
                or re-enacted code:"
        )
        print(df_conv.loc[~has_expected_og_re_code, ["id", "original_or_reenacted"]])
        df_conv = df_conv[has_expected_og_re_code]

    # Add columns to conversation DataFrame: language code, conversation number. Both
    # the language code and conversation number are extracted from the conversation ID.
    id_match_groups = df_conv["id"].str.extractall(conv_id_re_pattern)
    df_conv["lang_code"] = id_match_groups.lang_code.values
    df_conv["conv_num"] = id_match_groups.conv_num.values

    # Add column to conversation DataFrame: expected audio path.
    df_conv["audio_path"] = df_conv["id"].apply(
        lambda id: dir_input_recordings.joinpath(id + ".wav")
    )

    # Remove conversations with missing audio.
    has_existing_audio = df_conv["audio_path"].apply(lambda path: path.exists())
    if ~has_existing_audio.all():
        print("These conversations were ignored because their audio does not exist:")
        print(df_conv.loc[~has_existing_audio, ["id", "audio_path"]])
        df_conv = df_conv[has_existing_audio]

    # Add column to conversation DataFrame: expected markup path.
    df_conv["markup_path"] = df_conv["id"].apply(
        lambda id: dir_input_recordings.joinpath(id + ".eaf")
    )

    # Remove conversations with missing markup.
    has_existing_markup = df_conv["markup_path"].apply(lambda path: path.exists())
    if ~has_existing_markup.all():
        print("These conversations were ignored because their markup does not exist:")
        print(df_conv.loc[~has_existing_markup, ["id", "markup_path"]])
        df_conv = df_conv[has_existing_markup]

    # Add column to conversation DataFrame: path to write copy of audio.
    df_conv["copy_audio_path"] = df_conv["id"].apply(
        lambda id: dir_output_conv_audio.joinpath(f"{id}.wav")
    )

    def get_conv_trans_id(df_conv_row: pd.DataFrame) -> str:
        # Returns the inferred conversation ID of a conversation's translation, or None
        # if it could not be inferred. A conversation should have exactly one
        # translation with the same conversation number, a different language code, and
        # a different original or re-enacted code.
        # This function is nested because it refers to `df_conv` defined in the
        # enclosing scope.
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

    # Add column to conversation DataFrame: translation conversation ID.
    df_conv["trans_id"] = df_conv.apply(get_conv_trans_id, axis=1)

    # Remove conversations without translations.
    is_missing_translation = df_conv["trans_id"].isnull()
    if is_missing_translation.any():
        print("These conversations were ignored because they do not have translation:")
        print(df_conv.loc[is_missing_translation, ["id", "trans_id"]])
        df_conv = df_conv[~is_missing_translation]

    # Add column to conversation DataFrame: translation conversation language code.
    trans_id_match_groups = df_conv["trans_id"].str.extractall(conv_id_re_pattern)
    df_conv["trans_lang_code"] = trans_id_match_groups.lang_code.values

    return df_conv


def _get_markup_dataframes(
    df_conv_in: pd.DataFrame,
    dir_output_frag_audio_short: Path,
    dir_output_frag_audio_long: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    df_conv = df_conv_in.copy()

    # Read all markups (short fragments and long fragments) into a single DataFrame. Add
    # columns to markup DataFrame: source conversation ID, source conversation's
    # translation ID, source conversation language code, source conversation's
    # translation language code, conversation audio path, original or re-enacted code,
    # left participant unique ID, right participant unique ID.
    #
    # Appending to a list before converting to a DataFrame is faster than appending to a
    # DataFrame.
    df_markup_to_concat = []
    for conv in df_conv.itertuples():
        df_conv_markup = elan_to_dataframe(conv.markup_path)
        df_conv_markup["conv_id"] = conv.id
        df_conv_markup["trans_conv_id"] = conv.trans_id
        df_conv_markup["lang_code"] = conv.lang_code
        df_conv_markup["trans_lang_code"] = conv.trans_lang_code
        df_conv_markup["conv_audio_path"] = conv.audio_path
        df_conv_markup["original_or_reenacted"] = conv.original_or_reenacted
        df_conv_markup["participant_id_left"] = conv.participant_id_left
        df_conv_markup["participant_id_right"] = conv.participant_id_right
        df_conv_markup["participant_id_left_unique"] = conv.participant_id_left_unique
        df_conv_markup["participant_id_right_unique"] = conv.participant_id_right_unique
        df_markup_to_concat.append(df_conv_markup)
    df_markup = pd.concat(df_markup_to_concat)

    # Remove markups with unexpected value.
    has_expected_value = df_markup["markup_value"].str.fullmatch(
        shared.MARKUP_VAL_RE_PATTERN
    )
    # TODO Print whitespace in warning, or allow whitespace in markup value.
    if ~has_expected_value.all():
        print(
            "These markups were ignored because they have an unexpected value (whitespace might not be shown here)"
        )
        print(df_markup.loc[~has_expected_value, ["conv_id", "markup_value"]])
        df_markup = df_markup[has_expected_value]

    # Remove markups in unexpected tiers.
    has_expected_tier_name = df_markup["tier_name"].str.fullmatch(
        shared.MARKUP_TIER_PATTERN
    )
    if ~has_expected_tier_name.all():
        print("These markups were ignored because they are in an unexpected tier:")
        print(
            df_markup.loc[
                ~has_expected_tier_name, ["conv_id", "tier_name", "markup_value"]
            ]
        )
        df_markup = df_markup[has_expected_tier_name]

    # Remove duplicate markups (same source conversation and same markup value).
    cols_to_check_dupes = ["conv_id", "markup_value"]
    is_duplicate = df_markup.duplicated(cols_to_check_dupes, False)
    if is_duplicate.any():
        print("These markups were ignored because they have duplicate values:")
        print(df_markup.loc[is_duplicate, ["conv_id", "tier_name", "markup_value"]])
        df_markup = df_markup[~is_duplicate]

    # Convert markup DataFrame duration columns from milliseconds (float) to duration
    # (pandas Timedelta).
    df_markup["time_start"] = pd.to_timedelta(df_markup["time_start"], "ms")
    df_markup["time_end"] = pd.to_timedelta(df_markup["time_end"], "ms")

    # Add column to markup DataFrame: markup ID. A markup's ID is created from its
    # source conversation ID and its value.
    df_markup["id"] = df_markup["conv_id"] + "_" + df_markup["markup_value"]

    # Use the ID as the index and drop the column.
    df_markup.set_index("id", inplace=True, verify_integrity=True)

    # Add column to markup DataFrame: translation markup ID. The translation markup ID
    # is inferred, then checked in a later step.
    df_markup["trans_id"] = df_markup["trans_conv_id"] + "_" + df_markup["markup_value"]

    # Add column to markup DataFrame: duration.
    df_markup["duration"] = df_markup["time_end"] - df_markup["time_start"]

    # Remove markups without translation.
    has_translation = df_markup["trans_id"].isin(df_markup.index)
    if ~has_translation.all():
        print(
            "These markups were ignored because their translation markups were not \
                found:"
        )
        print(df_markup.loc[~has_translation, ["trans_id"]])
        df_markup = df_markup[has_translation]

    # Store the indices of markups belonging to short fragments and long fragments.
    is_short_frag = df_markup["tier_name"].isin(
        [shared.MARKUP_TIER_LEFT.name, shared.MARKUP_TIER_RIGHT.name]
    )
    is_long_frag = df_markup["tier_name"] == shared.MARKUP_TIER_BOTH.name

    # Split into two DataFrames. One for short fragments and another for long fragments.
    df_markup_short = df_markup[is_short_frag].copy()
    df_markup_long = df_markup[is_long_frag].copy()

    # Add column to short markup DataFrame: sox remix dictionary (to use when extracting
    # fragment audios later).
    df_markup_short["remix_dict"] = df_markup_short["tier_name"].apply(
        lambda tier_name: shared.MARKUP_TIERS_DICT[tier_name].remix_dict
    )

    # Add column to short markup DataFrame: track side code.
    df_markup_short["track_side_code"] = df_markup_short["tier_name"].apply(
        lambda tier_name: shared.MARKUP_TIERS_DICT[tier_name].track_side_code
    )

    # Add column to short markup DataFrame: participant ID of participant featured.
    def get_short_frag_participant_id(df_markup_short_row: pd.DataFrame) -> str:
        if df_markup_short_row.track_side_code == "l":
            return df_markup_short_row.participant_id_left
        if df_markup_short_row.track_side_code == "r":
            return df_markup_short_row.participant_id_right

    df_markup_short["participant_id"] = df_markup_short.apply(
        get_short_frag_participant_id, axis=1
    )

    # Add column to short markup DataFrame: unique participant ID of participant
    # featured.
    def get_short_frag_participant_id_unique(df_markup_short_row: pd.DataFrame) -> str:
        if df_markup_short_row.track_side_code == "l":
            return df_markup_short_row.participant_id_left_unique
        if df_markup_short_row.track_side_code == "r":
            return df_markup_short_row.participant_id_right_unique

    df_markup_short["participant_id_unique"] = df_markup_short.apply(
        get_short_frag_participant_id_unique, axis=1
    )

    # Add column to markup DataFrame: path to write fragment audio. Short fragment and
    # long fragment audios are written to separate directories.
    df_markup_short["audio_path"] = df_markup_short.index.map(
        lambda idx: dir_output_frag_audio_short.joinpath(f"{idx}.wav")
    )
    df_markup_long["audio_path"] = df_markup_long.index.map(
        lambda idx: dir_output_frag_audio_long.joinpath(f"{idx}.wav")
    )

    return df_markup_short, df_markup_long


def _get_participant_dataframe(
    path_input_metadata: Path, df_conv_in: pd.DataFrame
) -> pd.DataFrame:

    df_conv = df_conv_in.copy()

    df_participant = pd.read_excel(path_input_metadata, "participant")

    # Drop rows that contain NaN values. For each row to drop, print the column names
    # that contain NaN.
    cols_to_check_nan = [
        "id",
        "lang1",
        "lang2",
        "lang_strength",
        "dialect_note1",
        "dialect_note2",
        "conversation",
        "id_unique",
    ]
    row_contains_nan = df_participant[cols_to_check_nan].isna().any(axis=1)
    df_participant_nan = df_participant[row_contains_nan]
    if df_participant_nan.shape[0] > 0:
        print(
            "The following participant metadata rows were ignored because they contain NaN values:"
        )
        participant_metadata_row_start = 2
        for index, row in df_participant_nan.iterrows():
            index_adjusted = index + participant_metadata_row_start
            col_names_with_na = [
                name for name in cols_to_check_nan if pd.isna(row[name])
            ]
            print(f"\tRow {index_adjusted}: {col_names_with_na}")
        df_participant = df_participant.dropna(how="any")

    # Remove participants not featured in one or more conversations.
    is_featured_participant_left = df_participant["id_unique"].isin(
        df_conv["participant_id_left_unique"]
    )
    is_featured_participant_right = df_participant["id_unique"].isin(
        df_conv["participant_id_right_unique"]
    )
    is_featured_participant = (
        is_featured_participant_left | is_featured_participant_right
    )
    df_participant = df_participant[is_featured_participant]

    return df_participant


def _get_producer_dataframe(
    path_input_metadata: Path, df_conv_in: pd.DataFrame
) -> pd.DataFrame:

    df_conv = df_conv_in.copy()

    # Read the original producer metadata into a DataFrame.
    df_producer = pd.read_excel(path_input_metadata, "producer")

    # Drop rows that contain NaN values. For each row to drop, print the column names
    # that contain NaN.
    df_producer_nan = df_producer[df_producer.isna().any(axis=1)]
    if df_producer_nan.shape[0] > 0:
        print(
            "The following producer metadata rows were ignored because they contain NaN values:"
        )
        producer_metadata_row_start = 2
        for index, row in df_producer_nan.iterrows():
            index_adjusted = index + producer_metadata_row_start
            col_names_with_na = [name for name in row[row.isna()].index]
            print(f"\tRow {index_adjusted}: {col_names_with_na}")
        df_producer = df_producer.dropna(how="any")

    # Remove producers not featured in one or more conversations.
    is_featured_producer = df_producer["id"].isin(df_conv["producer_id"])
    df_producer = df_producer[is_featured_producer]

    return df_producer


if __name__ == "__main__":
    main()
