# Write notes on fragments from analysis to a text file. The fragments selected for
# analysis have notes starting with "[x]".

import re
from enum import Enum

import compute_similarity
import data
import pandas as pd

Similarity = Enum("Similarity", ["Positive", "Negative"])


def write_comparisons(
    similarity_type: Similarity, frag_id: str, df_similarity_en: pd.DataFrame
):

    pattern_note_general = re.compile(r"^([^E]+)")
    pattern_note = re.compile(r"(E[NS]_\d{3}_\d{1,2}) ([TF][PN])(.*?)DONE")
    N_COMPARISON_FRAGS = 4

    if similarity_type == Similarity.Positive:
        sort_ascending = True
    elif similarity_type == Similarity.Negative:
        sort_ascending = False
    else:
        raise ValueError("Invalid similarity type.")

    frag_row = df_similarity_en[frag_id].sort_values(ascending=sort_ascending)
    frag_row = frag_row.drop(frag_id)

    file_output.write(f"\t- {similarity_type}\n")

    for i in range(N_COMPARISON_FRAGS):
        frag_id_comp = frag_row.index[i]
        notes_comp = df_metadata.loc[frag_id_comp, "note_function"]

        file_output.write(f"\t\t- `{frag_id_comp}`\n")

        matches = pattern_note_general.findall(notes_comp)
        note_general = matches[0].strip() + ","

        matches = pattern_note.findall(notes_comp)
        for match in matches:
            comparison_id = match[0]
            if comparison_id != frag_id:
                continue
            comparison_judgement = match[1]
            comparison_note = match[2].strip()
            file_output.write(
                f"\t\t\t- {NOTES_PREFIX} {comparison_judgement} {note_general}, {comparison_note}\n"
            )


df_metadata = data.read_metadata()
df_features = data.read_features_en_es()
df_similarity_en = compute_similarity.similarity_by_language(df_features, "EN")

path_output = data.DIR_RELEASE.joinpath("fragments-notes.txt")
file_output = open(path_output, "w")

df_metadata["note_function"] = df_metadata["note_function"].fillna("")

# Get indices of anchor fragments.
bool_was_selected = df_metadata["note_function"].apply(lambda x: "[x]" in x)
idx_was_selected = df_metadata[bool_was_selected].index

NOTES_PREFIX = "**Notes:**"

# For each anchor fragment.
for frag_id in idx_was_selected:

    # Read the anchor fragment's notes. Ignore the "[x]".
    frag_notes = df_metadata.loc[frag_id, "note_function"]
    frag_notes = frag_notes.replace("[x]", "")

    file_output.write(f"- `{frag_id}`\n")
    file_output.write(f"\t- {NOTES_PREFIX} {frag_notes}\n")

    write_comparisons(Similarity.Positive, frag_id, df_similarity_en)
    write_comparisons(Similarity.Negative, frag_id, df_similarity_en)

    file_output.close()
