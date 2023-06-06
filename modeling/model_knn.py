# k-nearest neighbors regression model.

import metrics
import models_shared
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor


def main():

    df_en_train, df_en_test, df_es_train, df_es_test = models_shared.read_features()

    # EN to ES
    run_task(
        df_en_train,
        df_en_test,
        df_es_train,
        df_es_test,
        models_shared.Task.en_to_es,
    )

    # ES to EN
    run_task(
        df_es_train,
        df_es_test,
        df_en_train,
        df_en_test,
        models_shared.Task.es_to_en,
    )


def run_task(
    df_X_train: pd.DataFrame,
    df_X_test: pd.DataFrame,
    df_Y_train: pd.DataFrame,
    df_Y_test: pd.DataFrame,
    task: models_shared.Task,
):

    X_train_arr = df_X_train.to_numpy()
    X_test_arr = df_X_test.to_numpy()
    Y_train_arr = df_Y_train.to_numpy()
    Y_test_arr = df_Y_test.to_numpy()

    # The weight function "distance" weights points by the inverse of their distance.
    # The metric function is set to the same function used for scoring (currently mean
    # Euclidean distance).
    regressor = KNeighborsRegressor(
        n_neighbors=5, weights="distance", metric=metrics.euclidean_distance_1D
    )

    regressor.fit(X_train_arr, Y_train_arr)

    Y_pred_arr = regressor.predict(X_test_arr)

    score = metrics.mean_euclidean_distance(Y_test_arr, Y_pred_arr)
    print(f"Running task: {task}")
    print(f"Score: {score}")

    return score


if __name__ == "__main__":
    main()
