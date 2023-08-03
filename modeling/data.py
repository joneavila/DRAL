from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

DIR_ROOT = Path(__file__).parent.parent.resolve()


# Paths to outputs of DRAL post-processing scripts.
DIR_RELEASE = DIR_ROOT.joinpath("DRAL-corpus/release")
PATH_METADATA_SHORT_FULL = DIR_RELEASE.joinpath("fragments-short-full.csv")

# Paths to outputs of feature computation scripts.
PATH_FEATURES = DIR_RELEASE.joinpath("features/features.csv")
# PATH_SPEAKER_IDS = DIR_FEATURES.joinpath("speaker-ids.csv")

# Paths to outputs of models.
DIR_EXPERIMENTS = DIR_ROOT.joinpath("modeling/")

# Paths to outputs of feature correlation figure scripts.
DIR_FEATURE_CORRS = DIR_EXPERIMENTS.joinpath("feature-correlations")

# Paths to outputs of linear regression model.
DIR_LIN_REG_OUTPUT = DIR_EXPERIMENTS.joinpath("linear-regression")
PATH_LIN_REG_FEATS_TEST_EN_ES = DIR_LIN_REG_OUTPUT.joinpath("EN-to-ES-feats-test.csv")
PATH_LIN_REG_FEATS_TEST_ES_EN = DIR_LIN_REG_OUTPUT.joinpath("ES-to-EN-feats-test.csv")
PATH_LIN_REG_FEATS_PRED_EN_ES = DIR_LIN_REG_OUTPUT.joinpath("EN-to-ES-feats-pred.csv")
PATH_LIN_REG_FEATS_PRED_ES_EN = DIR_LIN_REG_OUTPUT.joinpath("ES-to-EN-feats-pred.csv")

# Paths to outputs of synthesis baseline model.
DIR_SYNTH_BASELINE_OUTPUT = DIR_EXPERIMENTS.joinpath("synthesis-baseline")
PATH_SYNTH_BASELINE_FEATS_TEST_EN_ES = DIR_SYNTH_BASELINE_OUTPUT.joinpath(
    "EN-to-ES-feats-test.csv"
)
PATH_SYNTH_BASELINE_FEATS_TEST_ES_EN = DIR_SYNTH_BASELINE_OUTPUT.joinpath(
    "ES-to-EN-feats-test.csv"
)
PATH_SYNTH_BASELINE_FEATS_PRED_EN_ES = DIR_SYNTH_BASELINE_OUTPUT.joinpath(
    "EN-to-ES-feats-pred.csv"
)
PATH_SYNTH_BASELINE_FEATS_PRED_ES_EN = DIR_SYNTH_BASELINE_OUTPUT.joinpath(
    "ES-to-EN-feats-pred.csv"
)

# Paths to outputs of naive baseline.
DIR_NAIVE_OUTPUT = DIR_EXPERIMENTS.joinpath("naive-baseline")
PATH_NAIVE_FEATS_TEST_EN_ES = DIR_NAIVE_OUTPUT.joinpath("EN-to-ES-feats-test.csv")
PATH_NAIVE_FEATS_TEST_ES_EN = DIR_NAIVE_OUTPUT.joinpath("ES-to-EN-feats-test.csv")
PATH_NAIVE_FEATS_PRED_EN_ES = DIR_NAIVE_OUTPUT.joinpath("EN-to-ES-feats-pred.csv")
PATH_NAIVE_FEATS_PRED_ES_EN = DIR_NAIVE_OUTPUT.joinpath("ES-to-EN-feats-pred.csv")

FEATURE_BASE_CODE_TO_NAMES = {
    "cr": "creakiness",
    "sr": "speaking rate",
    "tl": "low pitch",
    "th": "high pitch",
    "wp": "wide pitch range",
    "np": "narrow pitch range",
    "vo": "intensity",
    "le": "lengthening",
    "cp": "CPPS",
    "pd": "peak disalignment",
}


def read_metadata() -> pd.DataFrame:
    df_frags = pd.read_csv(PATH_METADATA_SHORT_FULL, index_col="id")
    df_frags["duration"] = pd.to_timedelta(df_frags["duration"])
    # TODO Convert "duration_synthesis" and other columns here.
    return df_frags


def write_metadata(df_frags: pd.DataFrame) -> None:
    df_frags.to_csv(PATH_METADATA_SHORT_FULL)


def read_features_en_es():
    # Read CSV containing computed features, output of feature computation scripts, and
    # return as two DataFrames, one per language, with matching rows.
    lang_code_en = "EN"
    lang_code_es = "ES"
    df_features = _features_csv_to_df(PATH_FEATURES)
    is_en = df_features.index.str.startswith(lang_code_en)
    df_features_en = df_features[is_en]
    frag_ids_en = list(df_features_en.index.values)
    frag_ids_es = [
        frag_id.replace(lang_code_en, lang_code_es) for frag_id in frag_ids_en
    ]
    df_features_es = df_features.loc[frag_ids_es]
    return df_features_en, df_features_es


def _features_csv_to_df(path_features_csv: Path) -> pd.DataFrame:
    # Read a fragments features CSV, created by MATLAB feature computation script, into
    # a pandas DataFrame. The column `Row` contains the fragment IDs.
    df_features = pd.read_csv(path_features_csv, index_col="Row")
    return df_features


def feature_cols_by_type(df_features: pd.DataFrame) -> dict:
    cols = list(df_features.columns)
    by_base_feature = {}
    by_span = {}
    for col in cols:
        base_feature, span = col.split("-", 1)
        by_base_feature.setdefault(base_feature, []).append(col)
        by_span.setdefault(span, []).append(col)
    return by_base_feature, by_span


def standardize_features(df_features: pd.DataFrame) -> pd.DataFrame:
    """Standardize features by removing the mean and scaling to unit variance.

    Arguments:
        df_features -- Computed features.

    Returns:
        Standardized computed features.
    """
    scaler = StandardScaler()
    arr_features_standardized = scaler.fit_transform(df_features)
    df_features_standardized = pd.DataFrame(
        arr_features_standardized, df_features.index, df_features.columns
    )

    return df_features_standardized


def feature_base_code_to_name(feature_base_code: str) -> str:
    return FEATURE_BASE_CODE_TO_NAMES[feature_base_code]
