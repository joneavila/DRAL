# This script transcribes DRAL English and Spanish short fragments pairs with OpenAI
# Whisper pre-trained speech recognition models. Its input is fragments-short-full.csv
# created by make_DRAL_release.py. Its output is an augmented metadata CSV file, adding
# the column `text`.

import subprocess
from pathlib import Path

import pandas as pd
import whisper
from sox import file_info
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from utils.dirs import make_dirs_in_path_if_not_exist
from utils.sox import resample


def main():
    tqdm.pandas()

    dir_dral_release = Path("/Users/jon/Documents/dissertation/DRAL-corpus/release")
    path_input_metadata = dir_dral_release.joinpath("fragments-short-full.csv")

    # Load the fragments metadata into a DataFrame.
    df_frags = pd.read_csv(path_input_metadata, index_col="id")

    df_frags = get_en_es_fragments(df_frags)

    # Resample to 16 kHz.
    sample_rate_hz = 16000
    dir_resampled_audio = dir_dral_release.joinpath(f"fragments-short-{sample_rate_hz}")
    df_frags = resample_fragments(df_frags, dir_resampled_audio, sample_rate_hz)

    df_frags = transcribe_fragments(df_frags)

    df_frags = mark_faulty_fragments(df_frags)

    # Overwrite the metadata with augmented metadata.
    df_frags.to_csv(path_input_metadata)


def get_en_es_fragments(df_frags: pd.DataFrame) -> pd.DataFrame:
    is_en_to_es = (df_frags["lang_code"] == "EN") & (
        df_frags["trans_lang_code"] == "ES"
    )
    idx_en_to_es = df_frags[is_en_to_es].index.tolist()
    idx_es_to_en = df_frags[is_en_to_es].trans_id.tolist()
    idx = idx_en_to_es + idx_es_to_en
    df_frags = df_frags.loc[idx]
    return df_frags


def resample_fragments(
    df_frags: pd.DataFrame, dir_output: Path, sample_rate_hz: float
) -> pd.DataFrame:
    # TODO Does the Midlevel Toolkit prefer the same sample rate?

    make_dirs_in_path_if_not_exist(dir_output)

    # Add a new column with the path to the resampled audio.
    def get_path_resampled(path_audio_str: str, dir_output: Path) -> str:
        path_audio = Path(path_audio_str)
        path_audio_resampled = dir_output.joinpath(f"{path_audio.name}")
        return str(path_audio_resampled)

    df_frags["audio_path_resampled"] = df_frags.apply(
        lambda frag: get_path_resampled(frag.audio_path, dir_output), axis=1
    )

    # Resample fragments in parallel.
    print("Resampling fragments...")
    n_frags = len(df_frags)
    process_map(
        resample,
        df_frags["audio_path"],
        df_frags["audio_path_resampled"],
        [sample_rate_hz] * n_frags,
        total=n_frags,
        chunksize=8,
    )

    return df_frags


def transcribe_fragments(df_frags: pd.DataFrame) -> pd.DataFrame:

    # If the fragments have been transcribed before, ignore fragments with existing
    # transcription, else transcribe all fragments.
    if "text" in df_frags.columns:
        to_transcribe = df_frags[df_frags["text"].isna()].index
    else:
        to_transcribe = df_frags.index

    print(f"Transcribing {len(to_transcribe)} fragments...")
    df_frags.loc[to_transcribe, "text"] = df_frags.loc[to_transcribe].progress_apply(
        lambda frag: transcribe_cpp(frag.lang_code, frag.audio_path_resampled), axis=1
    )

    return df_frags


def mark_faulty_fragments(df_frags: pd.DataFrame) -> pd.DataFrame:
    def is_bad_text(text: str):

        # Is always bad if empty.
        if pd.isna(text):
            return True

        allowed_chars = set(
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.…-,'\"$¿?¡!ÁáÉéÍíÓóÚúÜüÑñ "
        )
        return not set(text) <= allowed_chars

    has_bad_text = df_frags["text"].apply(is_bad_text)
    n_has_bad_text = has_bad_text.sum()
    print(f"{n_has_bad_text} fragments have bad text:")
    print(df_frags.loc[has_bad_text, "text"].to_string())

    # Get indices of fragments with bad text and their translations.
    idx_has_bad_text = df_frags[has_bad_text].index.values.tolist()
    idx_has_bad_text_trans = df_frags.loc[idx_has_bad_text, "trans_id"].tolist()
    idx_to_mark = list(set(idx_has_bad_text + idx_has_bad_text_trans))

    print(f"{len(idx_to_mark)} fragments (or translation) have bad text.")

    # Replace problem text with empty value.
    df_frags.loc[idx_to_mark, "text"] = None

    return df_frags


# Whisper transcription can be done within Python but is slow on Apple silicon. Instead,
# I use whisper.cpp, an optimized implementation. See the docs:
# - OpenAI Whisper: https://github.com/openai/whisper
# - whisper.cpp: https://github.com/ggerganov/whisper.cpp

# Whisper pre-trained models are either multilingual or English-only. "For
# English-only applications, the .en models tend to perform better"
# https://github.com/openai/whisper The "large" size does not have an English-only
# version.
# Load the English-only model to transcribe EN fragments.
# Load the multilingual model to transcribe ES fragments.


class WhisperException(Exception):
    pass


def transcribe_cpp(lang_code: str, path_audio_str: str) -> str:

    # Audio must be 16 kHz.
    sample_rate = file_info.sample_rate(path_audio_str)
    sample_rate_required_hz = 16000
    if int(sample_rate) != sample_rate_required_hz:
        raise WhisperException(f"Sample rate must be {sample_rate_required_hz} Hz.")

    path_whisper_cpp = Path("/Users/jon/Desktop/whisper.cpp")
    path_whisper_cpp_main = path_whisper_cpp.joinpath("main")
    path_whisper_cpp_model_en = path_whisper_cpp.joinpath("models/ggml-base.en.bin")
    path_whisper_cpp_model_es = path_whisper_cpp.joinpath("models/ggml-base.bin")

    if lang_code == "EN":
        path_whisper_cpp_model = path_whisper_cpp_model_en
        language = "en"
    elif lang_code == "ES":
        path_whisper_cpp_model = path_whisper_cpp_model_es
        language = "es"
    else:
        raise WhisperException("Unexpected language code.")

    completed_process = subprocess.run(
        args=[
            str(path_whisper_cpp_main),
            "--model",
            str(path_whisper_cpp_model),
            "--no-timestamps",
            "--file",
            path_audio_str,
            "--language",
            language,
        ],
        capture_output=True,
    )

    if completed_process.returncode != 0:
        print(completed_process.stderr)
        raise WhisperException("whisper.cpp return code was not zero.")

    # TODO Try `subprocess(encoding="utf-8") instead. See:
    # https://docs.python.org/3/library/subprocess.html
    std_out = completed_process.stdout
    std_out_decoded = str(std_out, "utf-8")
    std_out_decoded_striped = std_out_decoded.strip()

    transcription_text = std_out_decoded_striped

    return transcription_text


def transcribe(lang_code: str, path_audio_str: str) -> str:

    result = None
    if lang_code == "EN":
        model = whisper.load_model("small.en")
        language = "en"
    elif lang_code == "ES":
        model = whisper.load_model("small")
        language = "es"
    else:
        raise WhisperException("Unexpected language code.")

    result = model.transcribe(
        path_audio_str,
        language=language,
        condition_on_previous_text=False,
        without_timestamps=True,
        fp16=False,
    )

    transcription_text = result["text"]
    # transcription_language = result["language"]
    # transcription_segments = str(result["segments"])

    return transcription_text


if __name__ == "__main__":

    main()
