# The perfect model cheats and predicts the test data directly.

import metrics
import models_shared
import numpy as np
import pandas as pd


def main():
    df_en_train, df_en_test, df_es_train, df_es_test = models_shared.read_features()
    run_task(df_es_test, models_shared.Task.en_to_es)
    run_task(df_en_test, models_shared.Task.es_to_en)


def run_task(Y_test_df: pd.DataFrame, task: models_shared.Task) -> np.float64:
    print(f"Running task: {task}")
    Y_test_arr = Y_test_df.to_numpy()
    Y_pred_arr = Y_test_arr
    score = metrics.mean_euclidean_distance(Y_test_arr, Y_pred_arr)
    print(f"Score: {score}")


if __name__ == "__main__":
    main()
