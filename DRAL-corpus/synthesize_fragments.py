import subprocess
from pathlib import Path

import pandas as pd
import sox
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from utils.dirs import make_dirs_in_path_if_not_exist


class SynthesisException(Exception):
    pass


def main():

    tqdm.pandas()

    dir_dral_release = Path("/Users/jon/Documents/prosody_project/DRAL/release")

    # Read the input metadata into Pandas DataFrame, created by transcribe_fragments.py.
    input_metadata_path = dir_dral_release.joinpath("fragments-short-full.csv")
    df_frags = pd.read_csv(input_metadata_path, index_col="id")

    dir_output = dir_dral_release.joinpath("fragments-short-synthesis")
    df_frags = synthesize_fragments(df_frags, dir_output)

    # Overwrite the metadata with the augmented metadata.
    df_frags.to_csv(input_metadata_path)
    print(f"Done. Wrote to: {input_metadata_path}")


def synthesize_fragments(df_frags, dir_output: Path) -> pd.DataFrame:

    make_dirs_in_path_if_not_exist(dir_output)

    if "text" not in df_frags.columns:
        raise ("Metadata does not contain the column 'text' with transcriptions.")

    bool_has_text = df_frags["text"].notna()

    idx_has_text = df_frags[bool_has_text].index

    idx_lacks_text = df_frags[~bool_has_text].index
    print(f"{idx_lacks_text.size} fragments are missing text and will be ignored.")

    # If the metadata contains the column with synthesis audio path from a previous run,
    # ignore fragments with existing synthesis path.
    if "audio_path_synthesis" in df_frags.columns:
        bool_synth_present = df_frags["audio_path_synthesis"].notna()
        idx_has_synth = df_frags[bool_synth_present].index
        print(
            f"{idx_has_synth.size} fragments have synthesis audio and will be ignored."
        )
        idx_synth_missing = df_frags[~bool_synth_present].index
    else:
        idx_synth_missing = df_frags.index

    # Ignore fragments with missing text or present synth.
    idx_to_process = idx_has_text.intersection(idx_synth_missing)

    def get_path_synth(path_audio_str: str, dir_output: Path) -> str:
        path_audio = Path(path_audio_str)
        path_audio_synthesis = dir_output.joinpath(path_audio.name)
        return str(path_audio_synthesis)

    # Add a column with the path to store the synthesis audio if it succeeds.
    df_frags.loc[idx_to_process, "audio_path_synthesis"] = df_frags.loc[
        idx_to_process
    ].apply(lambda frag: get_path_synth(frag.audio_path, dir_output), axis=1)

    # Synthesize fragments.
    print(f"{idx_to_process.size} fragments to attempt synthesis.")
    process_map(
        text_to_speech,
        df_frags.loc[idx_to_process, "text"],
        df_frags.loc[idx_to_process, "lang_code"],
        df_frags.loc[idx_to_process, "audio_path_synthesis"],
        total=df_frags.loc[idx_to_process].shape[0],
        chunksize=1,
    )

    # If the output synthesis file exists, the synthesis succeeded.
    bool_synth_success = df_frags.loc[idx_to_process, "audio_path_synthesis"].apply(
        lambda path: Path(path).is_file()
    )
    idx_successful = idx_to_process[bool_synth_success]
    idx_failed = idx_to_process[~bool_synth_success]

    # If the synthesis failed, replace synthesis audio path with NaN.
    if not idx_failed.empty:
        print(
            f"{idx_failed.size} fragments had failed synthesis: {idx_failed.to_list()}"
        )
        df_frags.loc[idx_failed, "audio_path_synthesis"] = None

    def get_duration(path_audio: str):
        duration_seconds = sox.file_info.duration(path_audio)
        duration_timedelta = pd.to_timedelta(duration_seconds, "s")
        return duration_timedelta

    # Store duration of the synthesized audio as Timedelta for successful fragments.
    df_frags.loc[idx_successful, "duration_synthesis"] = df_frags.loc[
        idx_successful, "audio_path_synthesis"
    ].apply(get_duration)

    # If the synthesis has bad duration, replace path with NaN.
    duration_min = pd.Timedelta(0.3, "seconds")
    duration_max = pd.Timedelta(30, "seconds")
    bool_bad_duration = df_frags.loc[idx_successful, "duration_synthesis"].apply(
        lambda duration: (duration < duration_min) | (duration > duration_max)
    )
    idx_bad_duration = idx_successful[bool_bad_duration]
    if not idx_bad_duration.empty:
        print(
            f"{idx_bad_duration.size} fragments had bad duration: {idx_bad_duration.to_list()}"
        )
        df_frags.loc[idx_bad_duration, "audio_path_synthesis"] = None

    return df_frags


class CoquiException(Exception):
    pass


def text_to_speech(text: str, lang_code: str, path_output_str: str):

    # Coqui TTS functions. Coqui TTS has a Python API with limited support for Apple
    # silicon. Instead, this script uses the command line. To install, see docs:
    # https://github.com/coqui-ai/TTS

    # Ignore if output exists.
    path_output = Path(path_output_str)
    if path_output.exists():
        return

    # TODO Move this check to synthesis script.
    if pd.isna(text):
        return

    if lang_code == "EN":
        model_name = "tts_models/en/ljspeech/tacotron2-DDC"
    elif lang_code == "ES":
        model_name = "tts_models/es/mai/tacotron2-DDC"
    else:
        raise CoquiException("Unexpected language code.")

    # Run the Coqui TTS command.
    # TODO Check return code of return completed process.
    subprocess.run(
        [
            "tts",
            "--text",
            text,
            "--model_name",
            model_name,
            "--out_path",
            str(path_output),
        ],
        capture_output=True,
    )


if __name__ == "__main__":

    main()
