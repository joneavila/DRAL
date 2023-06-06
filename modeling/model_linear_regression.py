# Linear regression model.

from pathlib import Path

import matplotlib.pyplot as plt
import metrics
import models_shared
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def main():

    # TODO Read features from synthesis.

    dir_this_file = Path(__file__).parent.resolve()
    dir_output = dir_this_file.joinpath("linear-regression-outputs")

    print("***** Tasks with original data *****")
    dir_output_original = dir_output.joinpath("original")
    run_tasks_with_original_features(dir_output_original)

    print("***** Tasks with reduced data *****")
    dir_output_reduced = dir_output.joinpath("reduced")
    run_task_with_reduced_data(models_shared.Task.EN_TO_ES, dir_output_reduced)
    run_task_with_reduced_data(models_shared.Task.ES_TO_EN, dir_output_reduced)


def run_tasks_with_original_features(dir_output: Path):

    df_en_train, df_en_test, df_es_train, df_es_test = models_shared.read_features()

    # Use the EN partitions as the predictors and the ES partitions as the targets.
    _ = run_task(
        df_en_train,
        df_en_test,
        df_es_train,
        df_es_test,
        models_shared.Task.EN_TO_ES,
        dir_output,
    )

    # Use the ES partitions as the predictors and the EN partitions as the targets.
    _ = run_task(
        df_es_train,
        df_es_test,
        df_en_train,
        df_en_test,
        models_shared.Task.ES_TO_EN,
        dir_output,
    )


def run_task_with_reduced_data(task: models_shared.Task, dir_output: Path):
    # Increase the number of principal components, store results, and plot. Predict the
    # original features from the first N principal components, i.e. use the reduced
    # features as the predictors and the original features as the targets.

    dir_output.mkdir(parents=True, exist_ok=True)  # TODO Duplicate code from dirs.py.
    path_output_plot = dir_output.joinpath(f"plot-{task.name}.png")

    n_principal_components_min = 1
    n_principal_components_max = 100  # TODO This value is hard-coded.

    # Read the partitions using the original features.
    df_en_train, df_en_test, df_es_train, df_es_test = models_shared.read_features()

    # Read the partitions using the reduced features. This called function has an
    # optional argument for specifying the number of PCs to read, but it's faster to
    # read all PCs once and do the slicing later.
    (
        df_en_train_pca,
        df_en_test_pca,
        df_es_train_pca,
        df_es_test_pca,
    ) = models_shared.read_features_pca(n_principal_components_max)

    # The partitions for the original features versus PCA features should be identical
    # already, but no harm in checking.
    df_en_train.sort_index(inplace=True)
    df_en_train_pca.sort_index(inplace=True)
    assert df_en_train.index.equals(df_en_train_pca.index)
    df_en_test.sort_index(inplace=True)
    df_en_test_pca.sort_index(inplace=True)
    assert df_en_test.index.equals(df_en_test_pca.index)
    df_es_train.sort_index(inplace=True)
    df_es_train_pca.sort_index(inplace=True)
    assert df_es_train.index.equals(df_es_train_pca.index)
    df_es_test.sort_index(inplace=True)
    df_es_test_pca.sort_index(inplace=True)
    assert df_es_test.index.equals(df_es_test_pca.index)

    # To store scores for the different number of PCs.
    n_principal_components_scores = np.empty(n_principal_components_max)

    n_principal_components_range = range(
        n_principal_components_min, n_principal_components_max + 1
    )

    # Run the task with varying number of principal components.
    for n_principal_components in n_principal_components_range:

        if task is models_shared.Task.EN_TO_ES:
            df_X_train = df_en_train_pca
            df_X_test = df_en_test_pca
            df_Y_train = df_es_train
            df_Y_test = df_es_test
        elif task is models_shared.Task.ES_TO_EN:
            df_X_train = df_es_train_pca
            df_X_test = df_es_test_pca
            df_Y_train = df_en_train
            df_Y_test = df_en_test
        else:
            print("Error")  # TODO Replace with proper error.

        df_X_train = df_X_train.iloc[:, 0:n_principal_components]
        df_X_test = df_X_test.iloc[:, 0:n_principal_components]

        score_en_to_es_pca = run_task(
            df_X_train,
            df_X_test,
            df_Y_train,
            df_Y_test,
            task,
            dir_output=dir_output,
            write_output=False,
        )
        n_principal_components_idx = n_principal_components - 1
        n_principal_components_scores[n_principal_components_idx] = score_en_to_es_pca

    # Plot average error vs. number of principal components.
    # color_blue = "#45707A"  # gruvbox material light medium, blue
    # color_orange = "#C35E0A"  # gruvbox material light medium, orange
    color_black = "#000000"
    fig, ax = plt.subplots()
    ax.plot(
        n_principal_components_range, n_principal_components_scores, color=color_black
    )
    # Add a marker at the number of principal components with lowest average error.
    n_pcs_score_min_idx = n_principal_components_scores.argmin()
    n_pcs_score_min = n_principal_components_scores[n_pcs_score_min_idx]
    ax.plot(
        n_pcs_score_min_idx + 1,
        n_pcs_score_min,
        color=color_black,
        marker="o",
    )
    # Add texts.
    ax.set(
        xlabel="Number of predictors (Number of principal components)",
        ylabel="Average error (Average prosody dissimilarity)",
        title=f"Linear regression model, {task.name}\n"
        f"Average error at {n_principal_components_max} is "
        f"{n_principal_components_scores[n_principal_components_max-1]:.2f}, "
        f"lowest at {n_pcs_score_min_idx} is {n_pcs_score_min:.2f}",
    )
    ax.grid()
    fig.savefig(path_output_plot)


def run_task(
    df_X_train: pd.DataFrame,
    df_X_test: pd.DataFrame,
    df_Y_train: pd.DataFrame,
    df_Y_test: pd.DataFrame,
    task: models_shared.Task,
    dir_output: Path,
    write_output: bool = True,
) -> np.float64:

    print(f"Task: {task.name}")

    dir_output.mkdir(parents=True, exist_ok=True)  # TODO Duplicate code from dirs.py.
    path_output_coeffs = dir_output.joinpath(f"coeffs-{task.name}.csv")

    predictor_names = df_X_train.columns
    target_names = df_Y_train.columns

    X_train_arr = df_X_train.to_numpy()
    X_test_arr = df_X_test.to_numpy()
    Y_train_arr = df_Y_train.to_numpy()
    Y_test_arr = df_Y_test.to_numpy()

    regressor = train(X_train_arr, Y_train_arr)

    Y_pred_arr = predict(regressor, X_test_arr)

    pred_average_error = score(Y_pred_arr, Y_test_arr)
    print(f"Average error: {pred_average_error:.2f}")

    # TODO Write the test data to CSV.
    # TODO Write the predictions to CVS.

    # Write coefficients to CSV.
    if write_output is True:
        df_coeffs = pd.DataFrame(
            regressor.coef_,
            index=target_names,
            columns=predictor_names,
        )
        df_coeffs.to_csv(
            path_output_coeffs,
            # float_format="%.3f",
        )
        print(f"Coefficients written to: {path_output_coeffs}\n")

    return pred_average_error


def train(X_train_arr, Y_train_arr) -> LinearRegression:
    regressor = LinearRegression()
    regressor.fit(X_train_arr, Y_train_arr)
    return regressor


def predict(regressor: LinearRegression, X_test_arr: np.ndarray) -> np.ndarray:
    return regressor.predict(X_test_arr)


def score(Y_pred_arr, Y_test_arr) -> np.float64:
    return metrics.mean_euclidean_distance(Y_test_arr, Y_pred_arr)


if __name__ == "__main__":
    main()
