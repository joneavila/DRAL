# [!] This scripts reads data created by make_DRAL_release.py. Run make_DRAL_release.py
# before running this script.

from pathlib import Path
from typing import TextIO

import pandas as pd
import shared


def main():

    dir_this_file = Path(__file__).parent.resolve()
    dir_dral_release = dir_this_file.joinpath("release/")
    # TODO Read default DRAL release path from data.py.

    conv_csv_path = dir_dral_release.joinpath("conversation.csv")
    participant_csv_path = dir_dral_release.joinpath("participant.csv")
    short_frags_csv_path = dir_dral_release.joinpath("fragments-short.csv")
    long_frags_csv_path = dir_dral_release.joinpath("fragments-long.csv")

    # Read CSV files into pandas DataFrames.
    df_conv = pd.read_csv(conv_csv_path)
    df_participant = pd.read_csv(participant_csv_path)
    df_frags_short = pd.read_csv(short_frags_csv_path)
    df_frags_long = pd.read_csv(long_frags_csv_path)

    # Convert short fragments duration columns to pandas Timedelta.
    df_frags_short["time_start"] = pd.to_timedelta(df_frags_short["time_start"])
    df_frags_short["time_end"] = pd.to_timedelta(df_frags_short["time_end"])
    df_frags_short["duration"] = pd.to_timedelta(df_frags_short["duration"])

    # Convert long fragments duration columns to pandas Timedelta.
    df_frags_long["time_start"] = pd.to_timedelta(df_frags_long["time_start"])
    df_frags_long["time_end"] = pd.to_timedelta(df_frags_long["time_end"])
    df_frags_long["duration"] = pd.to_timedelta(df_frags_long["duration"])

    path_output = dir_dral_release.joinpath("stats.txt")
    with open(path_output, "w") as file_output:
        print_header("conversations", file_output)
        print_conversations(df_conv, file_output)

        print_header("participants", file_output)
        print_participants(df_participant, file_output)

        print_header('short fragments ("phrases")', file_output)
        print_fragments_short(df_frags_short, file_output)

        print_header('short fragments ("phrases") EN-ES only', file_output)
        print_fragments_short(df_frags_short, file_output, en_es_only=True)

        print_header('long fragments ("re-enactments")', file_output)
        print_fragments_long(df_frags_long, file_output)

    print(f"Wrote output to: {path_output}")

    # Print stats since 6.0 release. Excuse the dead code.
    # date_str = "2023-03-24"
    # conv_ids_after_date = df_conv[df_conv["recording_date"] >= date_str]["id"].tolist()
    # conv_ids_after_date.remove("ES_080")
    # conv_ids_after_date.remove("EN_080")
    # df_frags_short_before_date = df_frags_short[
    #     ~df_frags_short["conv_id"].isin(conv_ids_after_date)
    # ]
    # df_frags_short_after_date = df_frags_short[
    #     df_frags_short["conv_id"].isin(conv_ids_after_date)
    # ]
    # print_header("other stats")
    # print(
    #     "unique participants, up to 6.0",
    #     df_frags_short_before_date["participant_id_unique"].nunique(),
    # )
    #
    # # Count the number of shared participants between the two sets of short fragments.
    # unique_participants_before_date = df_frags_short_before_date[
    #     "participant_id_unique"
    # ].unique()
    # unique_partcipants_after_date = df_frags_short_after_date[
    #     "participant_id_unique"
    # ].unique()
    # unique_partcipants_after_date = set(unique_partcipants_after_date).difference(
    #     unique_participants_before_date
    # )
    # print(
    #     "unique participants, from 6.0 to 7.0",
    #     len(unique_partcipants_after_date),
    # )
    #
    # avg_before_date = len(df_frags_short_before_date) / len(
    #     unique_participants_before_date
    # )
    # avg_after_date = len(df_frags_short_after_date) / len(unique_partcipants_after_date)
    # print(avg_before_date, avg_after_date)
    #
    # print_header('long fragments ("re-enactments") from 6.0 to 7.0 release')
    # print_fragments_long(df_frags_long)


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

    # Print number of re-enacted conversations.
    n_re_conversations = df_conv[
        df_conv["original_or_reenacted"] == shared.CONV_CODE_REENACTED
    ].shape[0]
    file_output.write(f"count (re-enacted) = {n_re_conversations}\n")


def print_participants(df_participant: pd.DataFrame, file_output: TextIO) -> None:

    # Print number of unique participants.
    n_unique_participant_ids = df_participant["id_unique"].nunique()
    file_output.write(f"count (unique) = {n_unique_participant_ids}\n")


def print_fragments_short(
    df_frags_short: pd.DataFrame, file_output: TextIO, en_es_only: bool = False
) -> None:

    # Drop fragments that are not from EN-ES pairs. (DRAL 7.0 does not include any
    # short fragments pairs other than EN-ES, so this isn't very useful.)
    if en_es_only:
        is_en_frag = df_frags_short["id"].str.startswith("EN")
        frag_ids_en = df_frags_short["id"][is_en_frag].tolist()
        candidate_frag_ids_es = [frag_id.replace("EN", "ES") for frag_id in frag_ids_en]
        is_es_frag = df_frags_short["id"].isin(candidate_frag_ids_es)
        df_frags_short = df_frags_short[is_en_frag | is_es_frag]

    # Print number of original or re-enacted short fragments.
    n_frags = df_frags_short.shape[0]
    file_output.write(f"count (original or re-enacted) = {n_frags}\n")

    # Print number of original or re-enacted short fragments by language.
    for lang_code in shared.LANG_CODES:
        id_pattern = rf"^{lang_code}.*"
        series_frags_in_lang = df_frags_short["id"].str.fullmatch(id_pattern)
        n_in_lang = series_frags_in_lang.sum()
        file_output.write(f"\t{lang_code} count = {n_in_lang}\n")

    # Print number of original short fragments.
    n_frags_original = df_frags_short[
        df_frags_short["original_or_reenacted"] == "OG"
    ].shape[0]
    file_output.write(f"count (original) = {n_frags_original}\n")

    # Print number of re-enacted short fragments.
    n_frags_reenacted = df_frags_short[
        df_frags_short["original_or_reenacted"] == "RE"
    ].shape[0]
    file_output.write(f"count (re-enacted) = {n_frags_reenacted}\n")

    file_output.write("duration\n")

    # Print total duration of short fragments.
    duration_total = df_frags_short["duration"].sum()
    file_output.write(f"\ttotal = {duration_total}\n")

    # Print mean duration of short fragments.
    duration_mean = df_frags_short["duration"].mean()
    file_output.write(f"\tmean = {duration_mean}\n")

    # Print minimum duration of short fragments.
    duration_min = df_frags_short["duration"].min()
    file_output.write(f"\tminimum = {duration_min}\n")

    # Print maximum duration of short fragments.
    duration_max = df_frags_short["duration"].max()
    file_output.write(f"\tmaximum = {duration_max}\n")


def print_fragments_long(df_long_frags: pd.DataFrame, file_output: TextIO) -> None:

    # Print number of original or re-enacted long fragments.
    n_frags = df_long_frags.shape[0]
    file_output.write(f"count (original or re-enacted) =  {n_frags}\n")

    # Print number of original or re-enacted long fragments by language.
    for lang_code in shared.LANG_CODES:
        id_pattern = rf"^{lang_code}.*"
        df_frags_in_lang = df_long_frags["id"].str.fullmatch(id_pattern)
        n_in_lang = df_frags_in_lang.sum()
        file_output.write(f"\t{lang_code} count = {n_in_lang}\n")

    # Print number of original long fragments.
    n_frags_original = df_long_frags[
        df_long_frags["original_or_reenacted"] == "OG"
    ].shape[0]
    file_output.write(f"count (original) = {n_frags_original}\n")

    # Print number of re-enacted long fragments.
    n_frags_reenacted = df_long_frags[
        df_long_frags["original_or_reenacted"] == "RE"
    ].shape[0]
    file_output.write(f"count (re-enacted) = {n_frags_reenacted}\n")

    file_output.write("duration\n")

    # Print total duration of long fragments.
    duration_total = df_long_frags["duration"].sum()
    file_output.write(f"\ttotal = {duration_total}\n")

    # Print mean duration of long fragments.
    duration_mean = df_long_frags["duration"].mean()
    file_output.write(f"\tmean = {duration_mean}\n")

    # Print minimum duration of long fragments.
    duration_min = df_long_frags["duration"].min()
    file_output.write(f"\tminimum = {duration_min}\n")

    # Print maximum duration of long fragments.
    duration_max = df_long_frags["duration"].max()
    file_output.write(f"\tmaximum = {duration_max}\n")


if __name__ == "__main__":
    main()
