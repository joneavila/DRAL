# Make a figure with Pearson correlations between prosodic features, and save as an
# image. One figure per each language pair (EN-EN, EN-ES, ES-EN, ES-ES).
#
# The ES-EN figure will mirror the EN-ES figure.
#
# The number of base features (10) is hardcoded.

from pathlib import Path

import data
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main() -> None:

    df_features_raw_en, df_features_raw_es = data.read_features_en_es()

    plt.ioff()  # Disable interactive mode.

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

    # Create the output directory.
    data.DIR_FEATURE_CORRS.mkdir(parents=True, exist_ok=True)

    make_correlations_figure(
        coefs_en_en,
        df_features_en.columns,
        df_features_en.columns,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-en-en.png"),
        include_coef_labels=False,
    )

    make_correlations_figure(
        coefs_en_es,
        df_features_es.columns,
        df_features_en.columns,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-en-es.png"),
        include_coef_labels=False,
    )

    make_correlations_figure(
        coefs_es_en,
        df_features_en.columns,
        df_features_es.columns,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-es-en.png"),
        include_coef_labels=False,
    )

    make_correlations_figure(
        coefs_es_es,
        df_features_es.columns,
        df_features_es.columns,
        data.DIR_FEATURE_CORRS.joinpath("feature-correlations-es-es.png"),
        include_coef_labels=False,
    )


def make_correlations_figure(
    coefs: np.ndarray,
    x_labels: pd.Index,
    y_labels: pd.Index,
    path_output: Path,
    include_coef_labels: bool = True,
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

    # Alternatively, specify a diverging color map such as "RdYlGn" (red towards
    # negative, white towards center, and green towards positive), or
    # "twilight_shifted".
    res = axes.imshow(coefs_rounded, mpl.colormaps["pink"])  # type: ignore
    font_size_labels = 50

    # Add legend.
    clb = plt.colorbar(res, shrink=0.5)
    clb.ax.tick_params(labelsize=font_size_labels)

    # Set the X-axis and Y-axis tick locations and labels.
    # axes.set_xticks(np.arange(len(x_labels)), labels=x_labels)
    # axes.set_yticks(np.arange(len(y_labels)), labels=y_labels)

    # Instead, add a tick to separate the base features.
    lang_code_x = x_labels[0][:2]
    lang_code_y = y_labels[0][:2]
    x_labels = [
        f"{lang_code_x} {label}" for label in data.FEATURE_BASE_CODE_TO_NAMES.values()
    ]
    y_labels = [
        f"{lang_code_y} {label}" for label in data.FEATURE_BASE_CODE_TO_NAMES.values()
    ]

    axes.set_xticks(np.arange(4, 100, 10), labels=x_labels, fontsize=font_size_labels)
    axes.tick_params(axis="x", bottom=False)
    axes.set_yticks(np.arange(4, 100, 10), labels=y_labels, fontsize=font_size_labels)
    axes.tick_params(axis="y", bottom=False)

    #
    for i in range(10):
        for j in range(10):
            x1 = i * 10 - 0.5
            y1 = j * 10 - 0.5
            x2 = (i + 1) * 10
            y2 = (j + 1) * 10
            rec = plt.Rectangle(
                (x1, y1),
                x2,
                y2,
                fill=False,
                color="black",
                linewidth=2,
            )
            axes.add_patch(rec)

    # Rotate the tick labels.
    plt.setp(axes.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    plt.setp(axes.get_yticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add the coefficient values as text. Emphasize "significant" values with larger
    # text size and weight.
    if include_coef_labels:
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
