# Make a figure with Pearson correlations between prosodic features, and save as an
# image. One figure per each language pair (EN-EN, EN-ES, ES-EN, ES-ES).
#
# Notes:
# - The ES-EN figure will mirror the EN-ES figure.
# - The number of base features (10) is hardcoded.

from pathlib import Path
from typing import Optional

import data
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main() -> None:

    # Disable interactive mode.
    plt.ioff()

    # Create the output directory.
    data.DIR_FEATURE_CORRS.mkdir(parents=True, exist_ok=True)

    df_features_raw_en, df_features_raw_es = data.read_features_en_es()
    (
        df_coefs_en_en,
        df_coefs_en_es,
        df_coefs_es_en,
        df_coefs_es_es,
    ) = compute_feature_correlations(df_features_raw_en, df_features_raw_es)

    # Make a figure for each language pair, using the default style suitable for print.
    make_correlations_figure(
        df_coefs_en_en,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-en-en-print.png"),
    )
    make_correlations_figure(
        df_coefs_en_es,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-en-es-print.png"),
    )
    make_correlations_figure(
        df_coefs_es_en,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-es-en-print.png"),
    )
    make_correlations_figure(
        df_coefs_es_es,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-es-es-print.png"),
    )

    # Make a second figure for each language pair, using a style suitable for
    # presentations.
    make_correlations_figure(
        df_coefs_en_en,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-en-en-presentation.png"),
        group_features=False,
        show_coefficients=True,
    )
    make_correlations_figure(
        df_coefs_en_es,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-en-es-presentation.png"),
        group_features=False,
        show_coefficients=True,
    )
    make_correlations_figure(
        df_coefs_es_en,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-es-en-presentation.png"),
        group_features=False,
        show_coefficients=True,
    )
    make_correlations_figure(
        df_coefs_es_es,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-es-es-presentation.png"),
        group_features=False,
        show_coefficients=True,
    )

    # Make another English and Spanish figure with the (absoluate) difference between
    # using the full data and a subset.
    path_subset_4_0 = (
        Path(__file__).parent.resolve().joinpath("dral-4.0-short-frag-ids.csv")
    )
    df_features_raw_en_subset, df_features_raw_es_subset = data.read_features_en_es(
        path_subset=path_subset_4_0
    )
    (
        df_coefs_en_en_subset,
        df_coefs_en_es_subset,
        df_coefs_es_en_subset,
        df_coefs_es_es_subset,
    ) = compute_feature_correlations(
        df_features_raw_en_subset, df_features_raw_es_subset
    )
    # Get the absolute difference between the full and subset coefficients, to make a new DataFrame.
    # df_coefs_en_es_diff is another DataFrame with the same index and columns.
    df_coefs_en_es_diff = (df_coefs_en_es - df_coefs_en_es_subset).abs()
    make_correlations_figure(
        df_coefs_en_es_diff,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-en-es-diff-with-4.0.png"),
        color_map="Blues",
        data_range_min=0.0,
        data_range_max=0.5,
        group_features=False,
        show_coefficients=True,
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


def make_correlations_figure(
    df_coefs: pd.DataFrame,
    path_output: Path,
    color_map: str = "pink",
    data_range_min: Optional[float] = -1.0,
    data_range_max: Optional[float] = 1.0,
    group_features: bool = True,
    show_coefficients: bool = False,
) -> None:

    # Convert the values of df_coefs into a numpy array, round.
    coefs = df_coefs.values
    coefs_rounded = np.round_(coefs, 2)

    # Set x_labels to the column names, y_labels to the index names.
    x_labels = df_coefs.columns.tolist()
    y_labels = df_coefs.index.tolist()

    fig_size_width_pixels = 4096
    fig_size_height_pixels = fig_size_width_pixels
    pixel_in_inches = 1 / plt.rcParams["figure.dpi"]

    fig, axes = plt.subplots(
        figsize=(
            fig_size_width_pixels * pixel_in_inches,
            fig_size_height_pixels * pixel_in_inches,
        )
    )

    res = axes.imshow(coefs_rounded, mpl.colormaps[color_map], vmin=data_range_min, vmax=data_range_max)  # type: ignore

    font_size_labels = 50

    # Add legend.
    clb = plt.colorbar(res, shrink=0.5)
    clb.ax.tick_params(labelsize=font_size_labels)

    if group_features:
        # Add labels for the base features. Hide ticks.
        lang_code_x = x_labels[0][:2]
        lang_code_y = y_labels[0][:2]
        x_labels = [
            f"{lang_code_x} {label}"
            for label in data.FEATURE_BASE_CODE_TO_NAMES.values()
        ]
        y_labels = [
            f"{lang_code_y} {label}"
            for label in data.FEATURE_BASE_CODE_TO_NAMES.values()
        ]
        axes.set_xticks(
            np.arange(4, 100, 10), labels=x_labels, fontsize=font_size_labels
        )
        axes.tick_params(axis="x", bottom=False)
        axes.set_yticks(
            np.arange(4, 100, 10), labels=y_labels, fontsize=font_size_labels
        )
        axes.tick_params(axis="y", bottom=False)
    else:
        # Add labels and ticks for each feature.
        axes.set_xticks(np.arange(len(x_labels)), labels=x_labels)
        axes.set_yticks(np.arange(len(y_labels)), labels=y_labels)

    if group_features:
        # Add grid lines to separate the base features.
        for i in range(10):
            for j in range(10):
                x1 = i * 10 - 0.5
                y1 = j * 10 - 0.5
                x2 = (i + 1) * 10
                y2 = (j + 1) * 10
                rec = plt.Rectangle(  # type: ignore
                    (x1, y1),
                    x2,
                    y2,
                    fill=False,
                    color="black",
                    linewidth=2,
                )
                axes.add_patch(rec)

    if group_features:
        # Rotate axes labels 45 degrees.
        plt.setp(
            axes.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
        )
        plt.setp(
            axes.get_yticklabels(), rotation=45, ha="right", rotation_mode="anchor"
        )
    else:
        # Rotate x-axis labels 90 degrees.
        plt.setp(
            axes.get_xticklabels(), rotation=90, ha="right", rotation_mode="anchor"
        )

    if show_coefficients:
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

    # Write the figure as an image to the output path.
    fig.savefig(str(path_output))
    print(f"Output written to: {path_output}")


if __name__ == "__main__":
    main()
