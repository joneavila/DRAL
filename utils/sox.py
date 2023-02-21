# pysox functions. See docs: https://pysox.readthedocs.io/en/latest/index.html

from pathlib import Path

import pandas as pd
from sox import Combiner, Transformer


def trim_remix_audio(
    time_start: pd.Timedelta,
    time_end: pd.Timedelta,
    path_input: Path,
    path_output: Path,
    remix_dict: dict = None,
) -> None:
    """Trim an audio, optionally remix its channels, and create a new audio.

    Args:
        time_start (pd.Timedelta): Start time of the trim.
        time_end (pd.Timedelta): End time of the trim.
        path_input (Path): Path to input source audio.
        path_output (Path): Path to output audio.
        remix_dict (dict, optional): SoX remix dictionary for remixing channels.
            Defaults to None. For more information, see SoX documentation:
            https://sox.sourceforge.net/sox.html
    """
    transformer = Transformer()

    time_start_seconds = time_start.total_seconds()
    time_end_seconds = time_end.total_seconds()
    transformer.trim(time_start_seconds, time_end_seconds)

    # Apply additional effects only after trimming.
    if remix_dict is not None:
        transformer.remix(remix_dict)

    path_input_string = str(path_input)
    path_output_string = str(path_output)
    transformer.build(path_input_string, path_output_string)


def concatenate_audios(paths_input: list[Path], path_output: Path) -> None:
    """Concatenate audios, downsample to 16 kHz, and create a new audio.

    Args:
        paths_input (list[Path]): Paths of input audios.
        path_output (Path): Path to output audio.
    """

    combiner = Combiner()
    combiner.input_format = None  # Assume all input files are the same format.
    combiner.convert(16000)

    paths_input_string = [str(path) for path in paths_input]
    path_output_string = str(path_output)
    combiner.build(paths_input_string, path_output_string, "concatenate")


def is_mostly_silence(
    time_start: pd.Timedelta,
    time_end: pd.Timedelta,
    path_input: Path,
    remix_dict: dict = None,
) -> bool:
    """Estimate whether a fragment of an audio is mostly silence.

    Args:
        time_start (pd.Timedelta): Time when fragment begins.
        time_end (pd.Timedelta): Time when fragment ends.
        path_input (Path): Path to input source audio.
        remix_dict (dict, optional): SoX remix dictionary for remixing channels.
            Defaults to None. For more information, see SoX documentation:
            https://sox.sourceforge.net/sox.html

    Returns:
        bool: True if fragment is estimated 95 percent silence.
    """

    transformer = Transformer()

    # Trim the audio to just the fragment.
    time_start_seconds = time_start.total_seconds()
    time_end_seconds = time_end.total_seconds()
    transformer.trim(time_start_seconds, time_end_seconds)

    if remix_dict is not None:
        transformer.remix(remix_dict)

    # Get the duration of the fragment before removing portions of silence.
    stats_before = transformer.stat(str(path_input))
    duration_before = float(stats_before["Length (seconds)"])

    # Remove portions of silence.
    transformer.silence()

    # Get the duration of the fragment after removing portions of silence.
    stats_after = transformer.stat(str(path_input))
    duration_after = float(stats_after["Length (seconds)"])

    # Calculate the percentage of silence and return whether it is greater than the
    # maximum allowed.
    percent_silence = (duration_before - duration_after) / duration_before * 100
    percent_silence_allowed = 95
    return percent_silence > percent_silence_allowed


def resample(path_input: str, path_output_str: str, sample_rate_hz: float):
    """Resample an audio.

    Args:
        path_input (str): Path to input audio.
        path_output_str (str): Path to output audio.
        sample_rate_hz (float): Desired sample rate in Hz.
    """

    # Ignore if output exists.
    path_output = Path(path_output_str)
    if path_output.is_file():
        return

    transformer = Transformer()
    transformer.rate(sample_rate_hz)

    # make_dirs_in_path(path_audio_resampled.parent)
    transformer.build(path_input, path_output_str)
