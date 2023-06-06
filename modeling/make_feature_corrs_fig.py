# Make a figure with feature Pearson correlations and save as an image, one figure per
# each language pair (EN-EN, EN-ES, ES-EN, ES-ES). Features are computed by MATLAB
# feature computation script.

from pathlib import Path

import data
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main() -> None:

    df_features_raw_en = data.read_features_en()
    df_features_raw_es = data.read_features_es()

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

    make_correlations_figure(
        coefs_en_en,
        df_features_en.columns,
        df_features_en.columns,
        "DRAL EN-EN feature correlations",
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-EN-EN-DRAL-4.0.png"),
    )

    make_correlations_figure(
        coefs_en_es,
        df_features_es.columns,
        df_features_en.columns,
        "DRAL EN-ES feature correlations",
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-EN-ES-DRAL-4.0.png"),
    )

    # Note: The ES-EN figure will mirror the EN-ES figure.
    make_correlations_figure(
        coefs_es_en,
        df_features_en.columns,
        df_features_es.columns,
        "DRAL ES-EN feature correlations",
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-ES-EN-DRAL-4.0.png"),
    )

    make_correlations_figure(
        coefs_es_es,
        df_features_es.columns,
        df_features_es.columns,
        "DRAL ES-ES feature correlations",
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-ES-ES-DRAL-4.0.png"),
    )


def make_correlations_figure(
    coefs: np.ndarray,
    x_labels: pd.Index,
    y_labels: pd.Index,
    fig_title: str,
    path_output: Path,
) -> None:

    coefs_rounded = np.round_(coefs, 2)

    fig_size_width_pixels = 4096
    fig_size_height_pixels = fig_size_width_pixels
    pixel_in_inches = 1 / plt.rcParams["figure.dpi"]

    fig, axes = plt.subplots(
        figsize=(
            fig_size_width_pixels * pixel_in_inches,
            fig_size_height_pixels * pixel_in_inches,
        )
    )

    # Specify a diverging color map: red towards negative, white towards center, and
    # green towards positive.
    axes.imshow(coefs_rounded, plt.colormaps["RdYlGn"])

    # Set the X-axis and Y-axis tick locations and labels.
    axes.set_xticks(np.arange(len(x_labels)), labels=x_labels)
    axes.set_yticks(np.arange(len(y_labels)), labels=y_labels)

    # Rotate the X-axis tick labels 90 degrees.
    plt.setp(axes.get_xticklabels(), rotation=90, ha="right", rotation_mode="anchor")

    # Add the coefficient values as text. Emphasize "significant" values with larger
    # text size and weight.
    significant_threshold = 0.3
    for i in range(len(y_labels)):
        for j in range(len(x_labels)):
            coef = coefs_rounded[i, j]
            if abs(coef) >= significant_threshold:
                font_size = 7
                font_weight = "extra bold"
            else:
                font_size = 5
                font_weight = "normal"
            axes.text(
                j,
                i,
                coef,
                fontsize=font_size,
                ha="center",
                va="center",
                color="black",
                weight=font_weight,
            )

    # Set the axes title.
    axes.set_title(fig_title, fontsize=32)

    # Write the figure as an image to the output path.
    fig.savefig(path_output)
    print(f"Output written to: {path_output}")


if __name__ == "__main__":
    main()
