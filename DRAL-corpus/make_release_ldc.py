# Convert DRAL 8.0 to comply with LDC guidelines.
#
# - Create a root directory `Dialogs Re-enacted Across Languages`
# - Create a subdirectory `data/speech` to copy fragment audio files
# - Create a subdirectory `metadata` to copy metadata files
# - Create a subdirectory `docs` to manually store documentation files
#
# - Update fragment IDs in metadata and audio filenames
#   - Update short fragment IDs to include `S` after the conversation ID, e.g. from
#       `EN_001_1` to `EN_001_S_1`
#   - Update long fragment IDs to include `L` after the conversation ID and remove the
#       `#` before the annotation value, e.g. from `EN_001_#1` to `EN_001_L_1`
#
# - Exclude long fragment pairs that are not English-Spanish
# - Exclude conversation audios
#
# - Convert all audios to 16 kHz, 16-bit, FLAC
#
# See:
# - LDC Technical Guidelines: https://www.ldc.upenn.edu/data-management/providing-data/technical-guidelines
# - LDC Documentation Guidelines: https://www.ldc.upenn.edu/data-management/providing/documentation-guidelines
# - LDC Using LDC Data: https://www.ldc.upenn.edu/data-management/using

from pathlib import Path

import pandas as pd
import sox


def main():

    # Input paths.
    dir_this = Path(__file__).parent
    # Input paths: DRAL 8.0.
    dir_release = Path(__file__).parent.joinpath("release")
    path_frag_short = dir_release.joinpath("fragments-short.csv")
    path_frag_long = dir_release.joinpath("fragments-long.csv")
    path_conversation = dir_release.joinpath("conversation.csv")
    path_participant = dir_release.joinpath("participant.csv")
    path_producer = dir_release.joinpath("producer.csv")
    dir_frag_short_audio = dir_release.joinpath("fragments-short")
    dir_frag_long_audio = dir_release.joinpath("fragments-long")

    # Output paths.
    # Create a root directory in the output directory with the same name as the corpus
    # and its subdirectories.
    dir_out = dir_this.joinpath("release-ldc")
    dir_root_out = dir_out.joinpath("Dialogs Re-enacted Across Languages")
    dir_speech_data_out = dir_root_out.joinpath("data/speech")
    dir_metadata_out = dir_speech_data_out.joinpath("metadata")
    path_frag_short_out = dir_metadata_out.joinpath("fragments-short.csv")
    path_frag_long_out = dir_metadata_out.joinpath("fragments-long.csv")
    path_conversation_out = dir_metadata_out.joinpath("conversation.csv")
    path_participant_out = dir_metadata_out.joinpath("participant.csv")
    path_producer_out = dir_metadata_out.joinpath("producer.csv")
    dir_frag_short_audio_out = dir_speech_data_out.joinpath("fragments-short")
    dir_frag_long_audio_out = dir_speech_data_out.joinpath("fragments-long")
    dir_docs_data_out = dir_root_out.joinpath("docs")
    make_dirs_in_path(dir_metadata_out)
    make_dirs_in_path(dir_frag_short_audio_out)
    make_dirs_in_path(dir_frag_long_audio_out)
    make_dirs_in_path(dir_docs_data_out)

    print("Reading metadata...")
    df_frag_short = pd.read_csv(path_frag_short)
    df_frag_long = pd.read_csv(path_frag_long)
    df_conversation = pd.read_csv(path_conversation)
    df_participant = pd.read_csv(path_participant)
    df_producer = pd.read_csv(path_producer)

    print("Adding paritions metadata...")
    df_frag_short = add_partition_metadata(df_frag_short)
    df_frag_long = add_partition_metadata(df_frag_long)

    # DRAL 8.0 short fragment pairs are all English-Spanish, but long fragment pairs may
    # be in other language pairs. Drop the fragments that are not part of an
    # English-Spanish pair.
    #
    # Duplicate code in print_stats.py.
    print("Dropping non-English-Spanish fragment pairs...")
    is_en_with_es_pair = (df_frag_long["lang_code"] == "EN") & (
        df_frag_long["trans_id"].str.startswith("ES")
    )
    is_es_with_en_pair = (df_frag_long["lang_code"] == "ES") & (
        df_frag_long["trans_id"].str.startswith("EN")
    )
    is_part_of_pair = is_en_with_es_pair | is_es_with_en_pair
    df_frag_long = df_frag_long[is_part_of_pair]

    # Copy the "id" column to a temporary column "id_old".
    df_frag_short["id_old"] = df_frag_short["id"]
    df_frag_long["id_old"] = df_frag_long["id"]

    # Insert "S" into short fragment IDs, "L" into long fragment IDs, and delete any "#".
    print("Updating fragment IDs...")
    df_frag_short["id"] = df_frag_short["id"].apply(update_frag_id, to_insert="S")
    df_frag_short["trans_id"] = df_frag_short["trans_id"].apply(
        update_frag_id, to_insert="S"
    )
    df_frag_long["id"] = df_frag_long["id"].apply(update_frag_id, to_insert="L")
    df_frag_long["trans_id"] = df_frag_long["trans_id"].apply(
        update_frag_id, to_insert="L"
    )

    # Convert fragment audios to 16 kHz, 16-bit, FLAC.
    print("Converting fragment audios. This will take a while...")
    # TODO Parallelize and add progress bar with tqdm.
    tfm = sox.Transformer()
    tfm.convert(samplerate=16000, bitdepth=16)

    for _, row in df_frag_short.iterrows():
        path_audio_in = dir_frag_short_audio.joinpath(row["id_old"] + ".wav")
        path_audio_out = dir_frag_short_audio_out.joinpath(row["id"] + ".flac")
        tfm.build(str(path_audio_in), str(path_audio_out))

    for _, row in df_frag_long.iterrows():
        path_audio_in = dir_frag_long_audio.joinpath(row["id_old"] + ".wav")
        path_audio_out = dir_frag_long_audio_out.joinpath(row["id"] + ".flac")
        tfm.build(str(path_audio_in), str(path_audio_out))

    # Drop the "id_old" columns.
    df_frag_short.drop("id_old", axis=1, inplace=True)
    df_frag_long.drop("id_old", axis=1, inplace=True)

    # Write metadata to CSV files.
    print("Writing metadata...")
    df_frag_short.to_csv(path_frag_short_out, index=False)
    df_frag_long.to_csv(path_frag_long_out, index=False)
    df_conversation.to_csv(path_conversation_out, index=False)
    df_participant.to_csv(path_participant_out, index=False)
    df_producer.to_csv(path_producer_out, index=False)

    print("Done")


def add_partition_metadata(df_frag_in: pd.DataFrame) -> pd.DataFrame:
    # Add a column "set" with value "training" or "test". For DRAL 8.0, the training set
    # contains conversations 1-104 and the test set contains conversations 105-136.
    df_frag = df_frag_in.copy()

    conv_nums_training = range(1, 105)  # 1-104
    conv_nums_test = range(105, 137)  # 105-136

    def determine_set(frag_id: str) -> str:

        # The conversation number is the second element in the fragment ID, separated
        # by an underscore, e.g., "EN_001_3" is sourced from conversation 1.
        conv_num = int(frag_id.split("_")[1])
        if conv_num in conv_nums_training:
            return "training"
        elif conv_num in conv_nums_test:
            return "test"
        else:
            raise ValueError(f"Conversation number {conv_num} not in training or test.")

    df_frag["set"] = df_frag["id"].apply(determine_set)

    return df_frag


def update_frag_id(frag_id: str, to_insert: str):
    # Remove all pound characters from a fragment ID (used in long fragment IDs).
    frag_id_new = frag_id.replace("#", "")
    # Insert a string into a fragment ID, following the two-letter language code,
    # underscore, three-digit conversation ID, and second underscore.
    insert_idx = 7
    frag_id_new = f"{frag_id_new[:insert_idx]}{to_insert}_{frag_id_new[insert_idx:]}"
    return frag_id_new


def make_dirs_in_path(path: Path):
    path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
