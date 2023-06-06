# The synthesis baseline model estimates the translation of a fragment prosody
# representation by: transcribing the fragment's translation, synthesizing speech from
# the transcription, then computing its prosody representation.
# 
# Computing prosody representations at this point would require calling MATLAB code, so
# instead, the transcription, synthesis, and feature computation is done before calling
# this function, as part of the data workflow (see ../DRAL/README.md), hence the input
# argument `Y_test_synth_df`.
import pandas as pd


def test_synthesis_baseline(
    Y_test_df: pd.DataFrame, Y_test_synth_df: pd.DataFrame, test_type: TestType
) -> np.float64:

    Y_test_arr = Y_test_df.to_numpy()
    Y_test_synth_arr = Y_test_synth_df.to_numpy()
    Y_pred_arr = Y_test_synth_arr
    score = metrics.mean_euclidean_distance(Y_test_arr, Y_pred_arr)

    # TODO Borrowed from ../DRAL/utils/dirs.py.
    data.DIR_SYNTH_BASELINE_OUTPUT.mkdir(parents=True, exist_ok=True)

    if test_type == TestType.en_to_es:
        path_output_Y_test = data.PATH_SYNTH_BASELINE_FEATS_TEST_EN_ES
        path_output_Y_pred = data.PATH_SYNTH_BASELINE_FEATS_PRED_EN_ES
    elif test_type == TestType.es_to_en:
        path_output_Y_test = data.PATH_SYNTH_BASELINE_FEATS_TEST_ES_EN
        path_output_Y_pred = data.PATH_SYNTH_BASELINE_FEATS_PRED_ES_EN
    else:
        raise ValueError(f"Invalid test type: {test_type}")
    Y_test_df.to_csv(path_output_Y_test)
    print(f"Synthesis baseline test data written to: {path_output_Y_test}")
    Y_pred_df = pd.DataFrame(
        Y_pred_arr, index=Y_test_df.index, columns=Y_test_df.columns
    )
    Y_pred_df.to_csv(path_output_Y_pred)
    print(f"Synthesis baseline predictions written to: {path_output_Y_pred}")

    return score
