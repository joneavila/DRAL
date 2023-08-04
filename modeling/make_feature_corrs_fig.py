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
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main() -> None:

    # Disable interactive mode.
    plt.ioff()

    df_features_raw_en, df_features_raw_es = data.read_features_en_es()
    (
        df_coefs_en_en,
        df_coefs_en_es,
        df_coefs_es_en,
        df_coefs_es_es,
    ) = compute_feature_correlations(df_features_raw_en, df_features_raw_es)

    coefs = {
        "en-en": df_coefs_en_en,
        "en-es": df_coefs_en_es,
        "es-en": df_coefs_es_en,
        "es-es": df_coefs_es_es,
    }

    for lang_pair, df_coefs in coefs.items():

        # Make a figure for analysis.
        make_correlations_figure(
            df_coefs,
            data.DIR_FEATURE_CORRS.joinpath(f"feature-corrs-{lang_pair}-analysis.png"),
            group_features_labels=False,
            show_coeffs=True,
        )

        # Make a second figure for analysis, with significant coefficients only.
        make_correlations_figure(
            df_coefs,
            data.DIR_FEATURE_CORRS.joinpath(
                f"feature-corrs-{lang_pair}-analysis-sig-only.png"
            ),
            group_features_labels=False,
            show_coeffs=True,
            show_coeffs_sig_only=True,
        )

        # Make a figure for print.
        make_correlations_figure(
            df_coefs,
            data.DIR_FEATURE_CORRS.joinpath(f"feature-corrs-{lang_pair}-print.png"),
        )

        # Make a figure for aesthetics.
        make_correlations_figure(
            df_coefs,
            data.DIR_FEATURE_CORRS.joinpath(f"feature-corrs-{lang_pair}-pretty.png"),
            group_features_labels=False,
            group_features_grid=False,
            show_coeffs=False,
        )

    # Compute the correlations of a subset of the data (DRAL 4.0).
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
    # Make an English and Spanish figure.
    make_correlations_figure(
        df_coefs_en_es_subset,
        data.DIR_FEATURE_CORRS.joinpath(
            "feature-corrs-en-es-analysis-sig-only-4.0.png"
        ),
        group_features_labels=False,
        show_coeffs=True,
        show_coeffs_sig_only=True,
    )

    # Make an English and Spanish figure with the difference between using the full data
    # and a subset.
    df_coefs_en_es_diff = df_coefs_en_es - df_coefs_en_es_subset
    make_correlations_figure(
        df_coefs_en_es_diff,
        data.DIR_FEATURE_CORRS.joinpath("feature-corrs-en-es-diff-with-4.0.png"),
        color_map="bwr",
        data_range_min=-0.25,
        data_range_max=0.25,
        group_features_labels=False,
        show_coeffs=True,
        show_coeffs_sign=True,
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
    color_map: str = "PuOr",
    data_range_min: Optional[float] = -1.0,
    data_range_max: Optional[float] = 1.0,
    group_features_labels: bool = True,
    group_features_grid: bool = True,
    show_coeffs: bool = False,
    show_coeffs_sig_only: bool = False,
    show_coeffs_sign: bool = False,
) -> None:

    # Convert the values of df_coefs into a numpy array, round.
    coefs = df_coefs.values
    coefs_rounded = np.round_(coefs, 2)

    # Set x_labels to the column names, y_labels to the index names.
    x_labels = df_coefs.columns.tolist()
    y_labels = df_coefs.index.tolist()

    fig_size_width_pixels = 16384
    fig_size_height_pixels = fig_size_width_pixels
    pixel_in_inches = 1 / plt.rcParams["figure.dpi"]

    fig, axes = plt.subplots(
        figsize=(
            fig_size_width_pixels * pixel_in_inches,
            fig_size_height_pixels * pixel_in_inches,
        )
    )

    SIGNIFICANT_THRESHOLD = 0.3

    if show_coeffs_sig_only:
        # Set all non-significant coefficients to 0.
        coefs_rounded = np.where(
            np.abs(coefs_rounded) < SIGNIFICANT_THRESHOLD, 0, coefs_rounded
        )

    res = axes.imshow(coefs_rounded, mpl.colormaps[color_map], vmin=data_range_min, vmax=data_range_max)  # type: ignore

    FONT_LARGE_SIZE = 128
    FONT_SMALL_SIZE = 16
    FONT_SMALL_STROKE_WIDTH = 4

    # Add legend.
    clb = plt.colorbar(res, shrink=0.5)
    clb.ax.tick_params(labelsize=FONT_LARGE_SIZE)
    # clb.set_label(label="rho", size=FONT_LARGE_SIZE, weight="bold")

    if group_features_labels:
        # Add labels for the base features. Hide ticks.
        lang_code_x = x_labels[0][:2]
        lang_code_y = y_labels[0][:2]
        x_labels = [
            f"{lang_code_x} {label}"
            # for label in data.FEATURE_BASE_CODE_TO_NAMES.values()
            for label in data.FEATURE_BASE_CODE_TO_NAMES.keys()
        ]
        y_labels = [
            f"{lang_code_y} {label}"
            # for label in data.FEATURE_BASE_CODE_TO_NAMES.values()
            for label in data.FEATURE_BASE_CODE_TO_NAMES.keys()
        ]
        axes.set_xticks(
            np.arange(4, 100, 10), labels=x_labels, fontsize=FONT_LARGE_SIZE
        )
        axes.tick_params(axis="x", bottom=False)
        axes.set_yticks(
            np.arange(4, 100, 10), labels=y_labels, fontsize=FONT_LARGE_SIZE
        )
        axes.tick_params(axis="y", bottom=False)
        # Rotate axes labels 45 degrees.
        # plt.setp(
        #     axes.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
        # )
        # plt.setp(
        #     axes.get_yticklabels(), rotation=45, ha="right", rotation_mode="anchor"
        # )
    else:
        # Add labels and ticks for each feature.
        axes.set_xticks(
            np.arange(len(x_labels)),
            labels=x_labels,
            fontsize=FONT_SMALL_SIZE,
            weight="bold",
        )
        axes.set_yticks(
            np.arange(len(y_labels)),
            labels=y_labels,
            fontsize=FONT_SMALL_SIZE,
            weight="bold",
        )
        # Rotate x-axis labels 90 degrees.
        plt.setp(
            axes.get_xticklabels(), rotation=90, ha="right", rotation_mode="anchor"
        )

    if group_features_grid:
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
                    linewidth=8,
                )
                axes.add_patch(rec)

    if show_coeffs:
        for i in range(coefs_rounded.shape[0]):
            for j in range(coefs_rounded.shape[1]):
                coef = coefs_rounded[i, j]

                if show_coeffs_sign:
                    coef = f"{coef:+.2f}"

                if show_coeffs_sig_only and (abs(coef) < SIGNIFICANT_THRESHOLD):
                    continue
                # Add text for the coefficient.
                text = axes.text(
                    j,
                    i,
                    coef,
                    fontsize=FONT_SMALL_SIZE,
                    ha="center",
                    va="center",
                    color="black",
                    weight="bold",
                )
                text.set_path_effects(
                    [
                        PathEffects.withStroke(
                            linewidth=FONT_SMALL_STROKE_WIDTH, foreground="white"
                        )
                    ]
                )

    # # Create the output directory.
    # path_output.mkdir(parents=True, exist_ok=True)

    # Write the figure as an image to the output path.
    fig.savefig(str(path_output), bbox_inches="tight")
    print(f"Output written to: {path_output}")


if __name__ == "__main__":
    main()
