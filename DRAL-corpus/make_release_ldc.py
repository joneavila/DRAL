# Convert a DRAL release to the LDC format.
#
# - Create a root directory `Dialogs Re-enacted Across Languages`
# - Create a subdirectory `data/speech` to store fragment audios and metadata
# - Create a subdirectory `docs` to manually store documentation data later
#
# - Modify short fragment IDs to include `S` after the conversation ID
# - Modify long fragment IDs to include `L` after the conversation ID, and remove `#`
#   to avoid punctuation in filenames
#
# - Exclude long fragment pairs that are not English-Spanish
# - Exclude conversation audios
#
# - Convert all audios to 16 kHz, 16-bit, FLAC
# - Convert all metadata CSV files to XML
#
# See:
# - LDC Technical Guidelines: https://www.ldc.upenn.edu/data-management/providing-data/technical-guidelines
# - LDC Documentation Guidelines: https://www.ldc.upenn.edu/data-management/providing/documentation-guidelines
# - LDC Using LDC Data: https://www.ldc.upenn.edu/data-management/using

from pathlib import Path

import pandas as pd
import sox


def main():
    def convert_audio_frag_short(frag_id):
        path_audio_wav = dir_release.joinpath(f"fragments-short/{frag_id}.wav")
        frag_id_ldc = insert_code_into_id(frag_id, code="S")
        path_audio_flac = dir_output_audio_frags_short.joinpath(f"{frag_id_ldc}.flac")
        tfm.build(str(path_audio_wav), str(path_audio_flac))

    def convert_audio_frag_long(frag_id):
        path_audio_wav = dir_release.joinpath(f"fragments-long/{frag_id}.wav")
        frag_id_ldc = insert_code_into_id(frag_id, code="L")
        frag_id_ldc = remove_pound_from_id(frag_id_ldc)
        path_audio_flac = dir_output_audio_frags_long.joinpath(f"{frag_id_ldc}.flac")
        tfm.build(str(path_audio_wav), str(path_audio_flac))

    # TODO Read paths from command line arguments.
    # Input paths.
    dir_this = Path(__file__).parent
    dir_release = dir_this.joinpath("release")
    path_input_frags_short = dir_release.joinpath("fragments-short.csv")
    path_input_frags_long = dir_release.joinpath("fragments-long.csv")
    path_input_conversation = dir_release.joinpath("conversation.csv")
    path_input_participant = dir_release.joinpath("participant.csv")
    path_input_producer = dir_release.joinpath("producer.csv")

    # Output paths.
    # Name the root directory the same as the corpus.
    # Create the `speech` subdirectory, to store the audios and metadata.
    dir_output = dir_this.joinpath("release-ldc")
    dir_output_root = dir_output.joinpath("Dialogs Re-enacted Across Languages")
    dir_output_speech_data = dir_output_root.joinpath("data/speech")
    path_output_frags_short = dir_output_speech_data.joinpath("fragments-short.xml")
    path_output_frags_long = dir_output_speech_data.joinpath("fragments-long.xml")
    path_output_conversation = dir_output_speech_data.joinpath("conversation.xml")
    path_output_participant = dir_output_speech_data.joinpath("participant.xml")
    path_output_producer = dir_output_speech_data.joinpath("producer.xml")
    dir_output_audio_frags_short = dir_output_speech_data.joinpath("fragments-short")
    dir_output_audio_frags_long = dir_output_speech_data.joinpath("fragments-long")
    dir_output_docs_data = dir_output_root.joinpath("docs")
    make_dirs_in_path(dir_output_audio_frags_short)
    make_dirs_in_path(dir_output_audio_frags_long)
    make_dirs_in_path(dir_output_docs_data)

    # Configure SoX to convert audios to 16 kHz, 16-bit, FLAC.
    tfm = sox.Transformer()
    tfm.convert(samplerate=16000, bitdepth=16)

    # Read the metadata into DataFrames.
    df_frags_short = pd.read_csv(path_input_frags_short)
    df_frags_long = pd.read_csv(path_input_frags_long)
    df_conversation = pd.read_csv(path_input_conversation)
    df_participant = pd.read_csv(path_input_participant)
    df_producer = pd.read_csv(path_input_producer)

    # DRAL 7.0 short fragment pairs are all English-Spanish, but long fragment pairs may
    # be in other language pairs. Drop the fragments that are not part of an
    # English-Spanish pair.
    frag_ids_bad_lang = df_frags_long[
        (df_frags_long["lang_code"] != "EN") & (df_frags_long["lang_code"] != "ES")
    ].index
    frag_ids_bad_lang_trans = df_frags_long.iloc[frag_ids_bad_lang]["trans_id"].index
    frag_ids_to_drop = frag_ids_bad_lang.union(frag_ids_bad_lang_trans)
    df_frags_long.drop(frag_ids_to_drop, inplace=True)

    # Write fragment audios to FLAC.
    df_frags_short["id"].apply(convert_audio_frag_short)
    df_frags_long["id"].apply(convert_audio_frag_long)

    # Insert "S" into short fragment IDs and their translation fragment IDs.
    df_frags_short["id"] = df_frags_short["id"].apply(insert_code_into_id, code="S")
    df_frags_short["trans_id"] = df_frags_short["trans_id"].apply(
        insert_code_into_id, code="S"
    )
    # Insert "L" into long fragment IDs and their translation fragment IDs. Remove "#".
    df_frags_long["id"] = df_frags_long["id"].apply(insert_code_into_id, code="L")
    df_frags_long["trans_id"] = df_frags_long["trans_id"].apply(
        insert_code_into_id, code="L"
    )
    df_frags_long["id"] = df_frags_long["id"].apply(remove_pound_from_id)
    df_frags_long["trans_id"] = df_frags_long["trans_id"].apply(remove_pound_from_id)

    # Write metadata to XML.
    def dataframe_to_xml(df: pd.DataFrame, path_output: Path):
        df.to_xml(path_output, index=False, parser="etree")

    dataframe_to_xml(df_frags_short, path_output_frags_short)
    dataframe_to_xml(df_frags_long, path_output_frags_long)
    dataframe_to_xml(df_conversation, path_output_conversation)
    dataframe_to_xml(df_participant, path_output_participant)
    dataframe_to_xml(df_producer, path_output_producer)


def insert_code_into_id(frag_id: str, code: str):
    # Insert a string into a fragment ID, following the two-letter language code,
    # underscore, three-digit conversation ID, and second underscore.
    insert_idx = 7
    return f"{frag_id[:insert_idx]}{code}_{frag_id[insert_idx:]}"


def remove_pound_from_id(frag_id):
    # Remove all pound characters from a fragment ID (used in long fragment IDs).
    return frag_id.replace("#", "")


def make_dirs_in_path(path: Path):
    path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
