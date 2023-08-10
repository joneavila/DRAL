# These script is specific to DRAL 7.0.

from pathlib import Path

import pandas as pd


def main():

    # Input paths for fragment metadata.
    dir_release = Path(__file__).parent.resolve().joinpath("release")
    # Shared with others.
    path_frag_short = dir_release.joinpath("fragments-short.csv")
    path_frag_long = dir_release.joinpath("fragments-long.csv")
    # Dissertation work only.
    path_frag_short_complete = dir_release.joinpath("fragments-short-complete.csv")
    path_frag_long_complete = dir_release.joinpath("fragments-long-complete.csv")

    # Output paths for partitions metadata.
    path_frag_short_sets_out = dir_release.joinpath("fragments-short-sets.csv")
    path_frag_long_sets_out = dir_release.joinpath("fragments-long-sets.csv")

    # Shared with others.
    df_frag_short = pd.read_csv(path_frag_short)
    df_frag_long = pd.read_csv(path_frag_long)
    df_sets_short = create_partitions_metadata(df_frag_short)
    df_sets_long = create_partitions_metadata(df_frag_long)
    df_sets_short.to_csv(path_frag_short_sets_out, index=False)
    df_sets_long.to_csv(path_frag_long_sets_out, index=False)

    # Dissertation work only.
    df_frag_short_complete = pd.read_csv(path_frag_short_complete)
    df_frag_long_complete = pd.read_csv(path_frag_long_complete)
    df_frag_short_complete = append_partitions_to_frag_metadata(df_frag_short_complete)
    df_frag_long_complete = append_partitions_to_frag_metadata(df_frag_long_complete)
    df_frag_short_complete.to_csv(path_frag_short_complete, index=False)
    df_frag_long_complete.to_csv(path_frag_long_complete, index=False)


def determine_set(frag_id: str) -> str:

    # For DRAL 7.0, the training set contains conversations 1-104 and the test set
    # contains conversations 105-136.
    CONV_NUMS_TRAINING = range(1, 105)  # 1-104
    CONV_NUMS_TEST = range(105, 137)  # 105-136

    # The conversation number is the second element in the fragment ID, separated by an
    # underscore, e.g., "EN_001_3" is sourced from conversation 1.
    conv_num = int(frag_id.split("_")[1])
    if conv_num in CONV_NUMS_TRAINING:
        return "training"
    elif conv_num in CONV_NUMS_TEST:
        return "test"
    else:
        raise ValueError(f"Conversation number {conv_num} not in training or test.")


def append_partitions_to_frag_metadata(
    df_frag_in: pd.DataFrame,
) -> pd.DataFrame:
    # Add a column "set" with value "training" or "test" to fragment metadata.
    df_frag = df_frag_in.copy()
    df_frag["set"] = df_frag["id"].apply(determine_set)
    return df_frag


def create_partitions_metadata(df_frag_in: pd.DataFrame) -> pd.DataFrame:
    # Create a new metadata file to indicate which fragments are in the training and
    # test sets.
    df_sets = df_frag_in[["id"]].copy()
    df_sets["set"] = df_sets["id"].apply(determine_set)
    return df_sets


if __name__ == "__main__":

    main()
