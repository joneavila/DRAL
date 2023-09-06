# This script reads the metadata CSV file created by transcribe_fragments.py, and
# outputs an augmented file with an added "text_most_similar" column. The most similar
# fragments are found by computing the cosine similarity of the GloVe embeddings of the
# fragments' text.
#
# Install spaCy and the English pipeline. For example, on macOS:
#   pip install -U 'spacy[apple]'
#   python -m spacy download en_core_web_sm
# https://spacy.io/usage#installation

# TODO Compute the similarity for Spanish fragments.
# TODO Do not drop the Spanish fragments.
# TODO Accept input and output paths as arguments.

from pathlib import Path

import en_core_web_sm
import numpy as np
import pandas as pd


def cosine_similarity(v1: np.ndarray, v2: np.ndarray):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def drop_with_empty_text(df_frags):
    to_drop = df_frags["text"].isnull()
    if to_drop.any():
        print("Dropping fragments with empty text:")
        for _, row in df_frags[to_drop].iterrows():
            print(f"  {row['id']}")
    df_frags = df_frags.dropna(subset=["text"])
    return df_frags


def main() -> None:
    dir_this_file = Path(__file__).parent.resolve()
    dir_release = dir_this_file.joinpath("release")
    path_input_metadata = dir_release.joinpath("fragments-short-matlab-transcribed.csv")
    path_output_metadata = dir_release.joinpath(
        "fragments-short-matlab-transcribed-with-similarity.csv"
    )

    df_frags = pd.read_csv(path_input_metadata)

    df_frags_en = df_frags[df_frags["lang_code"] == "EN"]

    df_frags_en = drop_with_empty_text(df_frags_en)

    # Load default trained pipeline for English.
    nlp = en_core_web_sm.load()

    # Compute GloVe embeddings for each row.
    embeddings = df_frags_en["text"].apply(lambda x: nlp(x).vector)

    n_most_similar_to_print = 4

    for label, content in embeddings.items():
        print(label)
        # Compute the similarity of the current row with all others.
        similarity = embeddings.apply(lambda x: cosine_similarity(x, content))
        # Sort the values and get the indices.
        similar_sorted = similarity.sort_values(ascending=False).index
        # Get the three most similar rows.
        n_most_similar = similar_sorted[1 : n_most_similar_to_print + 1].tolist()
        # Create a string with the format "<id_1>: <text_1>; <id_2>: <text_2>; ...;
        # <id_n>: <text_n>"
        similar_texts_str = "; ".join(
            [
                f"{df_frags_en.at[index, 'id']}: {df_frags_en.at[index, 'text']}"
                for index in n_most_similar
            ]
        )
        df_frags_en.at[label, "text_most_similar"] = similar_texts_str

    df_frags_en.to_csv(path_output_metadata, index=False)


if __name__ == "__main__":
    main()
