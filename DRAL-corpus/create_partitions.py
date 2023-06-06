import argparse
import random
from pathlib import Path
from typing import Tuple

import pandas as pd

from consts import RANDOM_STATE_VAL


def main():
    dir_this_file = Path(__file__).parent.resolve()

    parser = argparse.ArgumentParser(
        description="Partition data into training and test sets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--path_metadata",
        help="Path to short fragment metadata. If the partitions will be read from MATLAB, specify the metadata output from prep_for_feature_comp.py.",
        default=dir_this_file.joinpath("release/fragments-short-matlab.csv"),
    )
    parser.add_argument(
        "-o",
        "--dir_output",
        help="Path to directory to write partitioned metadata to.",
        default=dir_this_file.joinpath("release/features"),
    )
    args = parser.parse_args()

    path_metadata = args.path_metadata
    dir_output = args.dir_output

    path_output_EN_train = dir_output.joinpath("EN-train.csv")
    path_output_EN_test = dir_output.joinpath("EN-test.csv")
    path_output_ES_train = dir_output.joinpath("ES-train.csv")
    path_output_ES_test = dir_output.joinpath("ES-test.csv")

    if (
        path_output_EN_train.exists()
        or path_output_EN_test.exists()
        or path_output_ES_train.exists()
        or path_output_ES_test.exists()
    ):
        print("Stopped because one or more partition files already exists.")
        return

    df_EN_train, df_EN_test, df_ES_train, df_ES_test = partition_data(path_metadata)

    df_EN_train.to_csv(path_output_EN_train)
    df_EN_test.to_csv(path_output_EN_test)
    df_ES_train.to_csv(path_output_ES_train)
    df_ES_test.to_csv(path_output_ES_test)


def partition_data(
    path_metadata: Path, test_fraction: float = 0.2
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Partition fragments into speaker-independent training and test sets, attempt to
    # achieve the specified split. This function can be called multiple times on the
    # same data and ouput the same partitions. The simple, maybe naive, algorithm is:
    #   1. Sort participants by their number of fragments, descending order.
    #   2. To the training set, add fragments from the first participants that have a
    #       cumulative sum less than or equal to the number of fragments needed to get
    #       closest to the specified split.
    #   3. To the test set, add fragments from the remaning participants.
    # Note: Producers have the largest number of fragments and are first to be added to
    # the training set.
    # TODO The participant ID unique column was changed from a string to an integer.

    assert 0 < test_fraction < 1

    # Set the random seed for reproducibility.
    random.seed(RANDOM_STATE_VAL)

    # TODO Duplicate code from data.py.
    df_frags = pd.read_csv(path_metadata, index_col="id")

    df_frags_EN = df_frags[df_frags["lang_code"] == "EN"]
    df_frags_ES = df_frags.loc[df_frags_EN["trans_id"]]

    n_samples_total = df_frags_EN.shape[0]
    n_samples_test_optimal = round(n_samples_total * test_fraction)
    n_samples_train_optimal = n_samples_total - n_samples_test_optimal

    speaker_ids_frags_count = df_frags_EN.value_counts(
        "participant_id_unique", sort=True
    )

    participant_mask = speaker_ids_frags_count.cumsum() <= n_samples_train_optimal

    speaker_ids_train = speaker_ids_frags_count[participant_mask]
    speaker_ids_test = speaker_ids_frags_count[~participant_mask]

    df_EN_train = df_frags_EN[
        df_frags_EN["participant_id_unique"].isin(speaker_ids_train.index)
    ]
    df_EN_test = df_frags_EN[
        df_frags_EN["participant_id_unique"].isin(speaker_ids_test.index)
    ]
    df_ES_train = df_frags_ES.loc[df_EN_train["trans_id"]]
    df_ES_test = df_frags_ES.loc[df_EN_test["trans_id"]]

    assert df_EN_train.shape == df_ES_train.shape
    assert df_EN_test.shape == df_ES_test.shape

    # Print some debugging info.
    n_samples_train = df_EN_train.shape[0]
    n_samples_test = df_EN_test.shape[0]
    print(f"{n_samples_total = }")
    print(f"{n_samples_train = } ({n_samples_train / n_samples_total * 100:.1f}%)")
    print(f"{n_samples_test = } ({n_samples_test / n_samples_total * 100:.1f}%)")
    print(f"{speaker_ids_train.index = }")
    print(f"{speaker_ids_test.index = }")

    return df_EN_train, df_EN_test, df_ES_train, df_ES_test


if __name__ == "__main__":

    main()
