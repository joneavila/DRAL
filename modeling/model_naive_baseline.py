# The naive baseline model simply outputs the same prosody features, i.e. assumes
# prosody should be kept exactly the same in translation.


import metrics
import models_shared
import pandas as pd


def main():
    df_en_train, df_en_test, df_es_train, df_es_test = models_shared.read_features()

    run_task(df_en_test, df_es_test, models_shared.Task.en_to_es)
    run_task(df_es_test, df_en_test, models_shared.Task.es_to_en)


def run_task(
    df_X_test: pd.DataFrame,
    df_Y_test: pd.DataFrame,
    task: models_shared.Task,
):

    print(f"Running task: {task}")

    arr_X_test = df_X_test.to_numpy()
    arr_Y_test = df_Y_test.to_numpy()
    arr_Y_pred = arr_X_test

    # Write predictions to CSV.
    # df_Y_pred = pd.DataFrame(
    #     arr_Y_pred, index=Y_test_df.index, columns=Y_test_df.columns
    # )
    # df_Y_pred.to_csv(path_output)

    pred_score = score(arr_Y_pred, arr_Y_test)
    print(f"Score: {pred_score}")


def score(Y_test_arr, Y_pred_arr):
    return metrics.mean_euclidean_distance(Y_test_arr, Y_pred_arr)
