from enum import Enum, auto
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.preprocessing import StandardScaler


class Task(Enum):
    EN_TO_ES = auto()
    ES_TO_EN = auto()


def read_features() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Read features computed with MATLAB.

    path_features = (
        "/Users/jon/Documents/dissertation/DRAL-corpus/release/features/features.csv"
    )
    df_features = pd.read_csv(path_features, index_col="Row")

    # path_idx_train = dir_release.joinpath("idx_test.csv")
    # path_idx_test = dir_release.joinpath("idx_test.csv")

    # TODO Temporary fix: Read the split DataFrames instead. In the future, only the IDs
    # will be stored in the CSVs. These are DataFrames with metadata.
    dir_release = Path("/Users/jon/Documents/dissertation/DRAL-corpus/release/")
    df_en_train = pd.read_csv(
        dir_release.joinpath("features/EN-train.csv"),
        index_col="id",
    )
    df_en_test = pd.read_csv(
        dir_release.joinpath("features/EN-test.csv"),
        index_col="id",
    )
    df_es_train = pd.read_csv(
        dir_release.joinpath("features/ES-train.csv"),
        index_col="id",
    )
    df_es_test = pd.read_csv(
        dir_release.joinpath("features/ES-test.csv"),
        index_col="id",
    )
    # Read the index (IDs) from them.

    # idx_train = pd.read_csv(path_idx_train)
    # idx_test = pd.read_csv(path_idx_test)

    # df_en = pd.read_csv(path_features_en)
    # df_es = pd.read_csv(path_features_es)

    # TODO Some fragments were dropped since the Interspeech data, so temporarily ignore
    # these.
    df_en_train = df_features.loc[df_en_train.index.intersection(df_features.index)]
    df_en_test = df_features.loc[df_en_test.index.intersection(df_features.index)]
    df_es_train = df_features.loc[df_es_train.index.intersection(df_features.index)]
    df_es_test = df_features.loc[df_es_test.index.intersection(df_features.index)]

    df_en_train_norm, df_en_test_norm = standardize_features(df_en_train, df_en_test)
    df_es_train_norm, df_es_test_norm = standardize_features(df_es_train, df_es_test)

    return df_en_train_norm, df_en_test_norm, df_es_train_norm, df_es_test_norm


def read_features_pca(n_principal_components: int = 8):
    # Input arguments:
    #   n_principal_components - the number of principal components to use, return when
    #   reading the rotated data (columns or principal components are already ordered by
    #   variance explained)
    # Read features computed with MATLAB (PCA workflow).

    dir_pca_output = Path(
        "/Users/jon/Documents/dissertation/DRAL-corpus/release/features"
    )
    path_features_en_train = dir_pca_output.joinpath(
        "PCA-outputs-EN/rotated-train-EN.csv"
    )
    path_features_en_test = dir_pca_output.joinpath(
        "PCA-outputs-EN/rotated-test-EN.csv"
    )
    path_features_es_train = dir_pca_output.joinpath(
        "PCA-outputs-ES/rotated-train-ES.csv"
    )
    path_features_es_test = dir_pca_output.joinpath(
        "PCA-outputs-ES/rotated-test-ES.csv"
    )

    # The MATLAB code reads the partitions and outputs separate files, so no need to split again here.
    # The columns (PCs) are ordered by variance.
    df_en_train = pd.read_csv(path_features_en_train, index_col="Row")
    df_en_test = pd.read_csv(path_features_en_test, index_col="Row")
    df_es_train = pd.read_csv(path_features_es_train, index_col="Row")
    df_es_test = pd.read_csv(path_features_es_test, index_col="Row")

    print(f"Number of principal components read: {n_principal_components}")
    df_en_train = df_en_train.iloc[:, 0:n_principal_components]
    df_en_test = df_en_test.iloc[:, 0:n_principal_components]
    df_es_train = df_es_train.iloc[:, 0:n_principal_components]
    df_es_test = df_es_test.iloc[:, 0:n_principal_components]

    # TODO Is the standardization step needed?

    return df_en_train, df_en_test, df_es_train, df_es_test


def standardize_features(
    df_train: pd.DataFrame, df_test: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Z-score normalization (standardization).

    # TODO Print the mean and standard deviation of the train and test sets, before and
    # after standardization, for debugging.

    # Standardize the features of the training data by removing the mean and scaling to
    # unit variance, then perform the centering and scaling on the test data.
    scaler = StandardScaler()
    arr_train_norm = scaler.fit_transform(df_train)
    arr_test_norm = scaler.transform(df_test)

    # Convert from NumPy arrays back to pandas DataFrames.
    column_labels = df_train.columns
    df_train_norm = pd.DataFrame(
        arr_train_norm, index=df_train.index, columns=column_labels
    )
    df_test_norm = pd.DataFrame(
        arr_test_norm, index=df_test.index, columns=column_labels
    )

    return df_train_norm, df_test_norm
