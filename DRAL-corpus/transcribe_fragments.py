# Transcribe DRAL English and Spanish short fragments with OpenAI Whisper models.
#
# The inputs are the single-speaker concatenated conversation audios
# (fragments-short-contatenated/*.wav) and metadata CSV file
# (`fragments-short-matlab.csv`). The output is an augmented metadata CSV file
# (`fragments-short-matlab-transcribed.csv`), adding the columns: text, segments.
#
# To improve the quality of transcriptions, each single-speaker conversation audio is
# transcribed, then the transcription segments are matched to the individual fragments.
#
# The previous version of this code used a second, C++ implementation of OpenAI Whisper
# (https://github.com/ggerganov/whisper.cpp), which is no longer needed for Apple
# silicon devices.

from pathlib import Path

import pandas as pd
import whisper
from tqdm import tqdm  # For progress bars.


class WhisperException(Exception):
    # Class for exceptions raised by OpenAI Whisper.
    pass


whisper_lang_to_model_name = {
    # The available models and languages are listed here:
    # https://github.com/openai/whisper#available-models-and-languages
    "en": "base.en",
    "es": "base",
}


def main():
    tqdm.pandas()

    dir_this_script = Path(__file__).parent

    dir_release = dir_this_script.joinpath("release")
    path_input_metadata = dir_release.joinpath("fragments-short-matlab.csv")

    df_frags = pd.read_csv(
        path_input_metadata,
        index_col="id",
    )

    # Convert the "time_start_rel" and "time_end_rel" columns to TimeDelta objects.
    df_frags["time_start_rel"] = pd.to_timedelta(df_frags["time_start_rel"])
    df_frags["time_end_rel"] = pd.to_timedelta(df_frags["time_end_rel"])

    # Transcribe the fragments one language at a time. The model is kept in memory
    # between transcriptions to speed up the process.
    df_frags_en = df_frags[df_frags["lang_code"] == "EN"]
    df_frags_es = df_frags[df_frags["lang_code"] == "ES"]

    # Transcribe using the first method.
    df_frags_en_transcribed = transcribe_frags_full_with_segments(
        df_frags_en, dir_release, "en"
    )
    df_frags_es_transcribed = transcribe_frags_full_with_segments(
        df_frags_es, dir_release, "es"
    )

    # Transcribe using the second method.
    df_frags_en_transcribed = transcribe_frags_by_utterance(
        df_frags_en, dir_release, "en"
    )
    df_frags_es_transcribed = transcribe_frags_by_utterance(
        df_frags_es, dir_release, "es"
    )

    # Combine the augmented DataFrames, sort by fragment ID.
    df_frags_transcribed = pd.concat(
        [df_frags_en_transcribed, df_frags_es_transcribed]
    ).sort_index()

    # Create column "text" that copies "text1" if available, otherwise "text2".
    df_frags_transcribed = df_frags
    df_frags_transcribed["text"] = df_frags_transcribed["text1"].fillna(
        df_frags_transcribed["text2"]
    )

    # Write the augmented metadata to CSV.
    path_out_metadata = path_input_metadata.parent.joinpath(
        f"{path_input_metadata.stem}-transcribed{path_input_metadata.suffix}"
    )
    df_frags_transcribed.to_csv(path_out_metadata)


def transcribe_frags_full_with_segments(
    df_frags: pd.DataFrame, dir_release: Path, whisper_lang_code: str
) -> pd.DataFrame:
    # Method 1 of transcribing fragments: Transcribe the full conversation audio, then
    # match the transcription segments to the individual fragments. Returns a DataFrame
    # with added columns "segments1" and "text1".

    model_name = whisper_lang_to_model_name[whisper_lang_code]

    model = whisper.load_model(model_name, in_memory=True)

    concat_audio_paths = pd.unique(df_frags["concat_audio_path"])
    for path_concat_audio in tqdm(concat_audio_paths, total=len(concat_audio_paths)):
        df_frags_conv = df_frags[df_frags["concat_audio_path"] == path_concat_audio]

        path_audio_full = dir_release.joinpath(path_concat_audio)

        try:
            result = model.transcribe(
                str(path_audio_full),
                language=whisper_lang_code,
                word_timestamps=True,
                verbose=True,
                condition_on_previous_text=False,  # Each conversation is transcribed independently.
                fp16=False,  # Apple silicon does not support fp16.
            )
        except WhisperException:
            print("Exception when transcribing fragment (TODO Handle)")
            continue

        segments = result["segments"]

        # Collect all "words" into a flat list.
        conversation_words = [word for segment in segments for word in segment["words"]]

        # Convert the "start" and "end" values to Timedelta.
        for word in conversation_words:
            word["start"] = pd.to_timedelta(word["start"], unit="s")
            word["end"] = pd.to_timedelta(word["end"], unit="s")

        # Sort df_frags_conv by time_start_rel.
        df_frags_conv = df_frags_conv.sort_values(by="time_start_rel")

        # Insert the words that fall within the time range of the row.
        for idx, row in df_frags_conv.iterrows():
            # Get the words that fall within the time range of the row.
            words = [
                word
                for word in conversation_words
                if row["time_start_rel"] <= word["start"] <= row["time_end_rel"]
            ]

            # Save the list words as a string.
            df_frags.loc[idx, "segments1"] = str(words)

            # Join the words into a string and insert.
            text = " ".join([word["word"] for word in words])
            df_frags.loc[idx, "text1"] = text

    return df_frags


def transcribe_frags_by_utterance(
    df_frags: pd.DataFrame, dir_release: Path, whisper_lang_code: str
) -> pd.DataFrame:
    # Method 2 of transcribing fragments: Transcribe each fragment independently. This
    # method is *significantly* slower. Returns a DataFrame with added columns
    # "segments2" and "text2".

    model_name = whisper_lang_to_model_name[whisper_lang_code]

    model = whisper.load_model(model_name, in_memory=True)

    concat_audio_paths = pd.unique(df_frags["concat_audio_path"])
    for path_concat_audio in tqdm(concat_audio_paths, total=len(concat_audio_paths)):
        df_frags_conv = df_frags[df_frags["concat_audio_path"] == path_concat_audio]

        df_frags_conv = df_frags_conv.sort_values(by="time_start_rel")

        # Iterate over the rows of df_frags_conv.
        for idx, row in df_frags_conv.iterrows():
            path_audio_full = dir_release.joinpath(row["audio_path"])

            try:
                result = model.transcribe(
                    str(path_audio_full),
                    language=whisper_lang_code,
                    word_timestamps=True,
                    verbose=True,
                    condition_on_previous_text=True,
                    fp16=False,  # Apple silicon does not support fp16.
                )
            except WhisperException:
                print("Exception when transcribing fragment (TODO Handle)")
                continue

            # Insert the words that fall within the time range of the row.
            df_frags.loc[idx, "segments2"] = str(result["segments"])
            df_frags.loc[idx, "text2"] = result["text"]

    return df_frags


if __name__ == "__main__":
    main()
