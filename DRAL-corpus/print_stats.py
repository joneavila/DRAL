# [!] This scripts reads data created by make_DRAL_release.py. Run make_DRAL_release.py
# before running this script.

import re
from pathlib import Path

import pandas as pd
import shared


def main():

    dir_this_file = Path(__file__).parent.resolve()
    dir_dral_release = dir_this_file.joinpath("/Volumes/shared/DRAL-releases/DRAL-7.0")

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

    print_header("conversations")
    print_conversations(df_conv)

    print_header("participants")
    print_participants(df_participant)

    print_header('short fragments ("phrases")')
    print_fragments_short(df_frags_short)

    print_header('long fragments ("re-enactments")')
    print_fragments_long(df_frags_long)

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


def print_header(header: str, decorator: str = "*") -> None:
    # Print a string surrounded by a decorator.
    decorator_len = 10
    print(decorator * decorator_len, header, decorator * decorator_len)


def print_conversations(df_conv: pd.DataFrame) -> None:
    # Print number of original conversations.
    n_og_conversations = df_conv[
        df_conv["original_or_reenacted"] == shared.CONV_CODE_ORIGINAL
    ].shape[0]
    print(f"count (original) = {n_og_conversations}")

    # Print number of re-enacted conversations.
    n_re_conversations = df_conv[
        df_conv["original_or_reenacted"] == shared.CONV_CODE_REENACTED
    ].shape[0]
    print(f"count (re-enacted) = {n_re_conversations}")


def print_participants(df_participant: pd.DataFrame) -> None:

    # Print number of unique participants.
    n_unique_participant_ids = df_participant["id_unique"].nunique()
    print(f"count (unique) = {n_unique_participant_ids}")


def print_fragments_short(df_frags_short: pd.DataFrame) -> None:

    # Print number of original or re-enacted short fragments.
    n_frags = df_frags_short.shape[0]
    print(f"count (original or re-enacted) = {n_frags}")

    # Print number of original or re-enacted short fragments by language.
    for lang_code in shared.LANG_CODES:
        id_pattern = re.compile(rf"^{lang_code}.*")
        df_frags_in_lang = df_frags_short["id"].str.fullmatch(id_pattern)
        n_in_lang = df_frags_in_lang.values.sum()
        print(f"\t{lang_code} count = {n_in_lang}")

    # Print number of original short fragments.
    n_frags_original = df_frags_short[
        df_frags_short["original_or_reenacted"] == "OG"
    ].shape[0]
    print(f"count (original) = {n_frags_original}")

    # Print number of re-enacted short fragments.
    n_frags_reenacted = df_frags_short[
        df_frags_short["original_or_reenacted"] == "RE"
    ].shape[0]
    print(f"count (re-enacted) = {n_frags_reenacted}")

    print("duration")

    # Print total duration of short fragments.
    duration_total = df_frags_short["duration"].sum()
    print(f"\ttotal = {duration_total}")

    # Print mean duration of short fragments.
    duration_mean = df_frags_short["duration"].mean()
    print(f"\tmean = {duration_mean}")

    # Print minimum duration of short fragments.
    duration_min = df_frags_short["duration"].min()
    print(f"\tminimum = {duration_min}")

    # Print maximum duration of short fragments.
    duration_max = df_frags_short["duration"].max()
    print(f"\tmaximum = {duration_max}")


def print_fragments_long(df_long_frags: pd.DataFrame) -> None:

    # Print number of original or re-enacted long fragments.
    n_frags = df_long_frags.shape[0]
    print(f"count (original or re-enacted) =  {n_frags}")

    # Print number of original or re-enacted long fragments by language.
    for lang_code in shared.LANG_CODES:
        id_pattern = re.compile(rf"^{lang_code}.*")
        df_frags_in_lang = df_long_frags["id"].str.fullmatch(id_pattern)
        n_in_lang = df_frags_in_lang.values.sum()
        print(f"\t{lang_code} count = {n_in_lang}")

    # Print number of original long fragments.
    n_frags_original = df_long_frags[
        df_long_frags["original_or_reenacted"] == "OG"
    ].shape[0]
    print(f"count (original) = {n_frags_original}")

    # Print number of re-enacted long fragments.
    n_frags_reenacted = df_long_frags[
        df_long_frags["original_or_reenacted"] == "RE"
    ].shape[0]
    print(f"count (re-enacted) = {n_frags_reenacted}")

    print("duration")

    # Print total duration of long fragments.
    duration_total = df_long_frags["duration"].sum()
    print(f"\ttotal = {duration_total}")

    # Print mean duration of long fragments.
    duration_mean = df_long_frags["duration"].mean()
    print(f"\tmean = {duration_mean}")

    # Print minimum duration of long fragments.
    duration_min = df_long_frags["duration"].min()
    print(f"\tminimum = {duration_min}")

    # Print maximum duration of long fragments.
    duration_max = df_long_frags["duration"].max()
    print(f"\tmaximum = {duration_max}")


if __name__ == "__main__":
    main()
