# This scripts reads metadata files created by make_release.py and outputs a stats text
# file to the same release directory.

from pathlib import Path
from typing import TextIO

import pandas as pd
import shared


def main():
    dir_this_file = Path(__file__).parent.resolve()
    dir_dral_release = dir_this_file.joinpath("release")

    conv_csv_path = dir_dral_release.joinpath("conversation.csv")
    participant_csv_path = dir_dral_release.joinpath("participant.csv")
    short_frags_csv_path = dir_dral_release.joinpath("fragments-short.csv")
    long_frags_csv_path = dir_dral_release.joinpath("fragments-long.csv")

    # Read CSV files into pandas DataFrames.
    df_conv = pd.read_csv(conv_csv_path)
    df_participant = pd.read_csv(participant_csv_path)
    df_frag_short = pd.read_csv(short_frags_csv_path)
    df_frag_long = pd.read_csv(long_frags_csv_path)

    # Convert short fragments duration columns to pandas Timedelta.
    df_frag_short["time_start"] = pd.to_timedelta(df_frag_short["time_start"])
    df_frag_short["time_end"] = pd.to_timedelta(df_frag_short["time_end"])
    df_frag_short["duration"] = pd.to_timedelta(df_frag_short["duration"])

    # Convert long fragments duration columns to pandas Timedelta.
    df_frag_long["time_start"] = pd.to_timedelta(df_frag_long["time_start"])
    df_frag_long["time_end"] = pd.to_timedelta(df_frag_long["time_end"])
    df_frag_long["duration"] = pd.to_timedelta(df_frag_long["duration"])

    path_output = dir_dral_release.joinpath("stats.txt")
    with open(path_output, "w") as file_output:
        print_header("conversations", file_output)
        print_conversations(df_conv, file_output)

        print_header("participants", file_output)
        print_participants(df_participant, file_output)

        print_header('short fragments ("phrases")', file_output)
        print_fragments_short(df_frag_short, file_output)

        print_header('short fragments ("phrases") EN-ES only', file_output)
        print_fragments_short(df_frag_short, file_output, en_es_only=True)

        print_header('long fragments ("re-enactments")', file_output)
        print_fragments_long(df_frag_long, file_output)

        print_header('long fragments ("phrases") EN-ES only', file_output)
        print_fragments_long(df_frag_long, file_output, en_es_only=True)

    print(f"Wrote output to: {path_output}")


def drop_non_en_es(df_frag_in: pd.DataFrame) -> pd.DataFrame:
    df_frag = df_frag_in.copy()
    is_en_with_es_pair = (df_frag["lang_code"] == "EN") & (
        df_frag["trans_id"].str.startswith("ES")
    )
    is_es_with_en_pair = (df_frag["lang_code"] == "ES") & (
        df_frag["trans_id"].str.startswith("EN")
    )
    is_part_of_pair = is_en_with_es_pair | is_es_with_en_pair
    df_frag = df_frag[is_part_of_pair]
    return df_frag


def print_header(header: str, file_output: TextIO, decorator: str = "*") -> None:
    # Print a string surrounded by a decorator.
    decorator_len = 10
    file_output.write(
        f"{decorator * decorator_len} {header} {decorator * decorator_len}\n"
    )


def print_conversations(df_conv: pd.DataFrame, file_output: TextIO) -> None:
    # Print number of original conversations.
    n_og_conversations = df_conv[
        df_conv["original_or_reenacted"] == shared.CONV_CODE_ORIGINAL
    ].shape[0]
    file_output.write(f"count (original) = {n_og_conversations}\n")

    # Print number of original conversations by language.
    for lang_code in shared.LANG_CODES:
        id_pattern = rf"^{lang_code}.*"
        series_conv_in_lang = df_conv["id"].str.fullmatch(id_pattern)
        n_in_lang = series_conv_in_lang.sum()
        file_output.write(f"\t{lang_code} count = {n_in_lang}\n")

    # Print number of re-enacted conversations.
    n_re_conversations = df_conv[
        df_conv["original_or_reenacted"] == shared.CONV_CODE_REENACTED
    ].shape[0]
    file_output.write(f"count (re-enacted) = {n_re_conversations}\n")

    # Print number of re-enacted conversations by language.
    for lang_code in shared.LANG_CODES:
        id_pattern = rf"^{lang_code}.*"
        series_conv_in_lang = df_conv["id"].str.fullmatch(id_pattern)
        n_in_lang = series_conv_in_lang.sum()
        file_output.write(f"\t{lang_code} count = {n_in_lang}\n")


def print_participants(df_participant: pd.DataFrame, file_output: TextIO) -> None:
    # Print number of unique participants.
    n_unique_participant_ids = df_participant["id_unique"].nunique()
    file_output.write(f"count (unique) = {n_unique_participant_ids}\n")


def print_fragments_short(
    df_frag_short: pd.DataFrame, file_output: TextIO, en_es_only: bool = False
) -> None:
    # Optionally exclude fragments that are not from EN-ES pairs. (DRAL 8.0 does not
    # include any short fragments pairs other than EN-ES, so this isn't very useful.)
    if en_es_only:
        df_frag_short = drop_non_en_es(df_frag_short)

    # Print number of original or re-enacted short fragments.
    n_frags = df_frag_short.shape[0]
    file_output.write(f"count (original or re-enacted) = {n_frags}\n")

    # Print number of original or re-enacted short fragments by language.
    for lang_code in shared.LANG_CODES:
        id_pattern = rf"^{lang_code}.*"
        series_frags_in_lang = df_frag_short["id"].str.fullmatch(id_pattern)
        n_in_lang = series_frags_in_lang.sum()
        file_output.write(f"\t{lang_code} count = {n_in_lang}\n")

    # Print number of original short fragments.
    n_frags_original = df_frag_short[
        df_frag_short["original_or_reenacted"] == "OG"
    ].shape[0]
    file_output.write(f"count (original) = {n_frags_original}\n")

    # Print number of re-enacted short fragments.
    n_frags_reenacted = df_frag_short[
        df_frag_short["original_or_reenacted"] == "RE"
    ].shape[0]
    file_output.write(f"count (re-enacted) = {n_frags_reenacted}\n")

    file_output.write("duration\n")

    # Print total duration of short fragments.
    duration_total = df_frag_short["duration"].sum()
    file_output.write(f"\ttotal = {duration_total}\n")

    # Print mean duration of short fragments.
    duration_mean = df_frag_short["duration"].mean()
    file_output.write(f"\tmean = {duration_mean}\n")

    # Print minimum duration of short fragments.
    duration_min = df_frag_short["duration"].min()
    file_output.write(f"\tminimum = {duration_min}\n")

    # Print maximum duration of short fragments.
    duration_max = df_frag_short["duration"].max()
    file_output.write(f"\tmaximum = {duration_max}\n")


def print_fragments_long(
    df_frag_long: pd.DataFrame, file_output: TextIO, en_es_only: bool = False
) -> None:
    # Optionally exclude fragments that are not from EN-ES pairs.
    if en_es_only:
        df_frag_long = drop_non_en_es(df_frag_long)

    # Print number of original or re-enacted long fragments.
    n_frags = df_frag_long.shape[0]
    file_output.write(f"count (original or re-enacted) =  {n_frags}\n")

    # Print number of original or re-enacted long fragments by language.
    for lang_code in shared.LANG_CODES:
        id_pattern = rf"^{lang_code}.*"
        df_frags_in_lang = df_frag_long["id"].str.fullmatch(id_pattern)
        n_in_lang = df_frags_in_lang.sum()
        file_output.write(f"\t{lang_code} count = {n_in_lang}\n")

    # Print number of original long fragments.
    n_frags_original = df_frag_long[
        df_frag_long["original_or_reenacted"] == "OG"
    ].shape[0]
    file_output.write(f"count (original) = {n_frags_original}\n")

    # Print number of re-enacted long fragments.
    n_frags_reenacted = df_frag_long[
        df_frag_long["original_or_reenacted"] == "RE"
    ].shape[0]
    file_output.write(f"count (re-enacted) = {n_frags_reenacted}\n")

    file_output.write("duration\n")

    # Print total duration of long fragments.
    duration_total = df_frag_long["duration"].sum()
    file_output.write(f"\ttotal = {duration_total}\n")

    # Print mean duration of long fragments.
    duration_mean = df_frag_long["duration"].mean()
    file_output.write(f"\tmean = {duration_mean}\n")

    # Print minimum duration of long fragments.
    duration_min = df_frag_long["duration"].min()
    file_output.write(f"\tminimum = {duration_min}\n")

    # Print maximum duration of long fragments.
    duration_max = df_frag_long["duration"].max()
    file_output.write(f"\tmaximum = {duration_max}\n")


if __name__ == "__main__":
    main()
