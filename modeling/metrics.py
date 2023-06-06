import numpy as np
import torch


def euclidean_distance_2D(X1: np.ndarray, X2: np.ndarray):
    difference = np.subtract(X1, X2)

    # The "axis" argument specifies the axis which to compute the vector norm, in this
    # case the rows. The "org" argument specifies the order of the norm, in this case
    # the 2-norm, or Euclidean norm: $||x||_2 := \sqrt{x_1^2 + \cdots + x_n^2}$
    euclidean_distances = np.linalg.norm(difference, axis=1)

    return euclidean_distances


def mean_euclidean_distance(X1: np.ndarray, X2: np.ndarray) -> np.float64:
    # Return the mean Euclidean distance of two NumPy multidimensional, homogeneous
    # arrays.
    # TODO Does this function always return np.float64? Is it ever passed DataFrames?
    euclidean_distances = euclidean_distance_2D(X1, X2)
    euclidean_distances_mean = np.mean(euclidean_distances)
    return euclidean_distances_mean


def euclidean_distance_1D(x1: np.ndarray, x2: np.ndarray) -> np.float64:
    # Used only by the k-NN regression model for now. The user-defined metric function
    # should "takes two arrays representing 1D vectors as inputs and must return one
    # value indicating the distance between those vectors"
    # https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsRegressor.html

    difference = np.subtract(x1, x2)

    # The "axis" argument specifies the axis which to compute the vector norm, in this
    # case the rows. The "org" argument specifies the order of the norm, in this case
    # the 2-norm, or Euclidean norm: $||x||_2 := \sqrt{x_1^2 + \cdots + x_n^2}$
    euclidean_distance = np.linalg.norm(difference)
    euclidean_distance_rounded = round(euclidean_distance, 3)
    return euclidean_distance_rounded


def mean_euclidean_distance_tensor(x, y):
    # Used only by the neural network model for now.
    # TODO Add type hints.
    differences = x - y
    differences_squared = differences**2
    differences_squared_sum = torch.sum(differences_squared, dim=1)
    differences_squared_sum_sqrt = torch.sqrt(differences_squared_sum)
    differences_squared_sum_sqrt_mean = torch.mean(differences_squared_sum_sqrt)
    return differences_squared_sum_sqrt_mean
