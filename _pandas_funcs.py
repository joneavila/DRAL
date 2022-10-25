# _pandas_funcs.py    October 19, 2022    Jonathan Avila

import pandas as pd


def remove_not_in_pattern(df_in: pd.DataFrame, col: str, expected_pattern: str) -> pd.DataFrame:
    # Remove rows in `df_in` where value `col` does not match `expected_pattern`.
    df = df_in.copy()
    is_expected_value = df[col].str.fullmatch(expected_pattern).notnull()
    if ~is_expected_value.all():
        print(
            f"These rows were removed because the value `{col}` does not match the "
            f"pattern {expected_pattern}:"
        )
        print(df[~is_expected_value])
        df = df[is_expected_value]
    return df


def remove_not_in_list(df_in: pd.DataFrame, col: str, expected_values: list) -> pd.DataFrame:
    # Remove rows in `df_in` where value `col` is not in `expected_values`.
    df = df_in.copy()
    is_expected_value = df[col].isin(expected_values)
    if ~is_expected_value.all():
        print(
            f"These rows were removed because the value `{col}` is not in "
            f"{expected_values}:"
        )
        print(df.loc[~is_expected_value])
        df = df[is_expected_value]
    return df


def remove_duplicates(df_in: pd.DataFrame, cols: list) -> pd.DataFrame:
    # Remove rows in `df_in` where all values in `cols` are equal.
    df = df_in.copy()
    is_duplicate = df.duplicated(cols, False)
    if is_duplicate.any():
        print(f"These rows were removed because they have duplicate values in {cols}:")
        print(df.loc[is_duplicate, cols])
        df = df[~is_duplicate]
    return df


def remove_not_shared_in_col(df_in: pd.DataFrame, col: str, shared_col: str) -> pd.DataFrame:
    # Remove rows in `df_in` where values in `col` are not shared in `shared_col`.
    df = df_in.copy()
    is_shared = df[col].isin(df[shared_col])
    if ~is_shared.all():
        print(
            f"These rows were removed because the value `{col}` is not shared in "
            f"`{shared_col}`:"
        )
        print(df.loc[~is_shared])
        df = df[is_shared]
    return df


def remove_file_not_found(df_in: pd.DataFrame, col: str) -> pd.DataFrame:
    # Remove rows in `df_in` where value `col` is not a file that exists.
    df = df_in.copy()
    is_existing_file = df[col].apply(lambda path: path.exists())
    if ~is_existing_file.all():
        print(f"These rows were removed because value `{col}` (file) does not exist:")
        print(df[~is_existing_file])
        df = df[is_existing_file]
    return df


def remove_missing(df_in: pd.DataFrame, col: str) -> pd.DataFrame:
    # Remove rows in `df_in` where value `col` is missing (Nan, None, NaN, or NaT).
    df = df_in.copy()
    is_missing = df[col].isnull()
    if is_missing.any():
        print(f"These rows were removed because the value `{col}` is missing:")
        print(df[is_missing])
        df = df[~is_missing]
    return df
