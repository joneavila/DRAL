# Compute the Spearman correlations between fragment duration and features. Make a
# figure with the correlations, along with mean correlation of features by base feature
# and features by span, and write to PNG.

import data
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df_features_raw = data.read_features_en_es()
df_features = data.standardize_features(df_features_raw)

df_frags = data.read_metadata()

# Ignore the fragments without computed features (some fragments are filtered before
# the feature computation).
df_frags_with_features = df_frags[df_frags.index.isin(df_features.index)]

# Convert the fragment durations from Timedelta to seconds in float.
duration_td = df_frags_with_features["duration"]
duration_seconds = duration_td.transform(pd.Timedelta.total_seconds)

corr_method = "spearman"
coefs = df_features.corrwith(duration_seconds, axis=0, method=corr_method)
coefs = coefs.round(2)

print(f"Correlation method: {corr_method}")
print(f"Mean: {coefs.mean():+.2f}")
print(f"Maximum: {coefs.max():+} ({coefs.idxmax()})")
print(f"Minimum: {coefs.min():+} ({coefs.idxmin()})")

by_base_feature, by_span = data.feature_cols_by_type(df_features)

# TODO Duplicate code (will be displayed in figure).
print("Mean correlation by base feature:")
for base_feature, cols_with_base_feature in by_base_feature.items():
    coef_mean = coefs.loc[cols_with_base_feature].mean()
    coef_mean_rounded = round(coef_mean, 2)
    print(f"\t{coef_mean_rounded:+} {base_feature}")

# TODO Duplicate code (will be displayed in figure).
print("Mean correlation by span:")
for span, cols_with_span in by_span.items():
    coef_mean = coefs.loc[cols_with_span].mean()
    coef_mean_rounded = round(coef_mean, 2)
    print(f"\t{coef_mean_rounded:+} {span}")

# One subplot per base feature.
fig, axes = plt.subplots(nrows=len(by_base_feature), figsize=[16, 16])
fig.suptitle(f"{corr_method} correlation: duration vs. features", fontsize=16)

for ax, (base_feature, cols_with_base_feature) in zip(axes, by_base_feature.items()):

    # Hide the axes labels.
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    ax.set_title(data.feature_base_code_to_name(base_feature), fontsize=12)

    # Expand the coefficients to the full length of the fragment.
    expanded = np.empty(100)
    for col in cols_with_base_feature:
        coef = coefs.loc[col]
        idx_start = int(col.split("-")[1])
        idx_end = int(col.split("-")[2])
        expanded[idx_start:idx_end] = coefs[col]
        ax.text(
            (idx_start + idx_end) / 2,
            0.5,
            f"{coef:+}",
            ha="center",
            va="center",
            fontsize=12,
        )

    # Specify a diverging color map.
    ax.imshow((expanded, expanded), "coolwarm", vmin=-1, vmax=1, aspect=2)

    # Add the mean of base feature.
    pos = ax.get_position()
    coefs_mean = coefs.loc[cols_with_base_feature].mean()
    x = pos.x1 + 0.01
    y = (pos.y0 + pos.y1) / 2
    fig.text(x, y, f"{coefs_mean:+.2f}", fontsize=12)

# Add the mean of spans.
# TODO This code is hacky. It assumes the feature set uses the same spans.
for span, cols_with_span in by_span.items():
    coef_mean = coefs.loc[cols_with_span].mean()
    coef_mean_rounded = round(coef_mean, 2)
    idx_start = int(span.split("-")[0])
    idx_end = int(span.split("-")[1])
    # Use the last subplot as reference. This assumes each base feature has the same
    # number of spans and lengths.
    pos = axes[9].get_position()
    x0 = pos.x0
    x1 = pos.x1
    y = pos.y0 - 0.02
    x = ((idx_start + idx_end) / 2 / 100) * (x1 - x0) + x0
    fig.text(x, y, f"{coef_mean_rounded:+.2f}", fontsize=12)


# Write the figure to output path.
path_output_fig = data.DIR_FEATURES.joinpath("duration-correlations.png")
fig.savefig(path_output_fig)
print(f"Wrote figure: {path_output_fig}")
