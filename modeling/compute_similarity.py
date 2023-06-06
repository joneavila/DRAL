import numpy as np
import pandas as pd
from metrics import euclidean_distance_2D


class SimilarityException(Exception):
    pass


def similarity_to_mean(df_features: pd.DataFrame) -> pd.Series:
    """Compute the similarity of each fragment to the mean of all fragments.

    Arguments:
        df_features -- A DataFrame with fragment IDs as the index and features as
        columns.

    Returns:
        A pandas Series with index of fragment IDs and values of similarity to the mean.
    """
    arr_features = df_features.to_numpy()
    arr_mean = np.mean(arr_features, axis=0)
    arr_similarities = euclidean_distance_2D(arr_mean, arr_features)
    series_similarity_to_mean = pd.Series(arr_similarities, index=df_features.index)
    series_similarity_to_mean.sort_values(inplace=True)
    return series_similarity_to_mean


def similar_pairs(df_similarities: pd.DataFrame) -> pd.DataFrame:
    """Compute the most similar pairs of fragments.

    Arguments:
        df_similarities -- A symmetric DataFrame with fragment IDs as the index and
        columns and similarity scores as values. Returned by fragment_by_fragment().

    Returns:
        A DataFrame with three columns: "frag_id1", "frag_id2", and "similarity_score".
    """
    df_similarities_copy = df_similarities.copy()
    arr_similarities = df_similarities_copy.to_numpy()

    # Replace the diagonal and upper triangle with NaN. The diagonal is the similarity
    # between a fragment and itself. The upper triangle is the similarity between a
    # fragment and a fragment that has already been compared to it. These similarity
    # scores will be dropped later.
    arr_similarities[np.triu_indices(arr_similarities.shape[0])] = np.nan

    # Sort the fragment-to-fragment similarities and store these in a DataFrame with the
    # first column being the fragment ID of the first fragment, the second column being
    # the fragment ID of the second fragment, and the third column being the similarity
    # score.
    idx_sorted_flattened = np.argsort(arr_similarities, axis=None)
    idx_sorted_row, idx_sorted_col = np.unravel_index(
        idx_sorted_flattened, arr_similarities.shape
    )
    sorted_rows = df_similarities_copy.index[idx_sorted_row]
    sorted_cols = df_similarities_copy.columns[idx_sorted_col]
    sorted_scores = arr_similarities[(idx_sorted_row, idx_sorted_col)]
    df_similarity_pairs = pd.DataFrame(
        np.stack((sorted_rows, sorted_cols, sorted_scores), axis=1),
        columns=["frag_id1", "frag_id2", "similarity_score"],
    )

    # Drop the similarity scores that are NaN.
    df_similarity_pairs.dropna(inplace=True)

    return df_similarity_pairs


def similarity(df_features: pd.DataFrame) -> pd.DataFrame:
    """Compute the similarity between each fragment.

    Arguments:
        df_features -- A DataFrame with fragment IDs as the index and features as
        columns.

    Returns:
        A symmetric DataFrame with fragment IDs as the index and columns and similarity
        scores as values.
    """

    # Convert features to a Numpy array.
    arr_features = df_features.to_numpy()

    # Empty array to store similarity scores.
    arr_similarity = np.empty([df_features.shape[0], df_features.shape[0]])

    for i in range(arr_features.shape[0]):
        row = arr_features[i, :]
        arr_similarity[i, :] = euclidean_distance_2D(row, arr_features)

    # Store in a DataFrame.
    df_similarity = pd.DataFrame(
        arr_similarity,
        index=df_features.index,
        columns=df_features.index,
        dtype="float32",
    )

    return df_similarity


def similarity_by_language(df_features: pd.DataFrame, lang_code: str) -> pd.DataFrame:
    # Like similarity, but drop fragments that are not in the specified language.
    df_features = df_features[df_features.index.str.startswith(lang_code)]
    df_similarity = similarity(df_features)
    return df_similarity
