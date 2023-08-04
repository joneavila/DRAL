import data
import numpy as np
import pandas as pd


def main():

    df_features_raw_en, df_features_raw_es = data.read_features_en_es()
    (
        _,
        df_coefs_en_es,
        _,
        _,
    ) = compute_feature_correlations(df_features_raw_en, df_features_raw_es)

    # Rotate the coefficients so that the EN feature names are the index, and the ES
    # feature names are the columns.
    df_coefs_en_es_rotated = df_coefs_en_es.T

    # Sort by absolute value in descending order, then sort the original values using
    # the same order, and write to a file.
    df_coefs_en_es_abs = df_coefs_en_es_rotated.abs()
    series_coefs_en_es_abs_sorted = df_coefs_en_es_abs.unstack().sort_values(
        ascending=False
    )  # type: ignore
    series_coefs_en_es_sorted = df_coefs_en_es_rotated.unstack().loc[
        series_coefs_en_es_abs_sorted.index
    ]
    path_output_sorted_abs = data.DIR_FEATURE_CORRS.joinpath(
        "feat-corrs-en-es-by-abs.csv"
    )
    series_coefs_en_es_sorted.to_csv(
        path_output_sorted_abs,
        header=["rho"],
        sep="\t",
        float_format="%.2f",
    )

    # Without any sorting, the values are in the same order as the original feature (by
    # base feature).
    series_coefs_en_es = df_coefs_en_es_rotated.unstack(level=-1)
    path_output_sorted_base_code = data.DIR_FEATURE_CORRS.joinpath(
        "feat-corrs-en-es-by-base-code.csv"
    )
    series_coefs_en_es.to_csv(
        path_output_sorted_base_code,
        header=["rho"],
        sep="\t",
        float_format="%.2f",
    )


def compute_feature_correlations(
    df_features_raw_en, df_features_raw_es
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    df_features_en = data.standardize_features(df_features_raw_en)
    df_features_es = data.standardize_features(df_features_raw_es)

    # Append language code to column names.
    df_features_en.rename(lambda col_name: "EN-" + col_name, axis=1, inplace=True)
    df_features_es.rename(lambda col_name: "ES-" + col_name, axis=1, inplace=True)

    # Get a matrix of Pearson product-moment correlation coefficients.
    coefs = np.corrcoef(df_features_en, df_features_es, rowvar=False)

    # The matrix contains the coefficients for all features, so separate these into
    # language pairs.
    n_en_features = df_features_en.shape[1]
    n_es_features = df_features_es.shape[1]
    assert n_en_features == n_es_features
    n_features = n_en_features
    coefs_en_en = coefs[0:n_features, 0:n_features]
    coefs_en_es = coefs[0:n_features, n_features:]
    coefs_es_en = coefs[n_features:, 0:n_features]
    coefs_es_es = coefs[n_features:, n_features:]

    # Read the coefficients into DataFrames, setting their index and column names to
    # the feature names.
    df_coefs_en_en = pd.DataFrame(
        coefs_en_en, index=df_features_en.columns, columns=df_features_en.columns
    )
    df_coefs_en_es = pd.DataFrame(
        coefs_en_es, index=df_features_en.columns, columns=df_features_es.columns
    )
    df_coefs_es_en = pd.DataFrame(
        coefs_es_en, index=df_features_es.columns, columns=df_features_en.columns
    )
    df_coefs_es_es = pd.DataFrame(
        coefs_es_es, index=df_features_es.columns, columns=df_features_es.columns
    )

    return df_coefs_en_en, df_coefs_en_es, df_coefs_es_en, df_coefs_es_es


if __name__ == "__main__":
    main()
