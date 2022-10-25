# _sox_funcs.py    October 19, 2022    Jonathan Avila

from pathlib import Path

import pandas as pd
from sox import Combiner, Transformer


def build_audio(time_start: pd.Timedelta, time_end: pd.Timedelta, in_path: Path, out_path: Path, remix_dict: dict) -> None:
    # Clip the audio at `in_path` from `time_start` to `time_end`, remix channels with
    # `remix_dict`, and write to `out_path`.
    transformer = Transformer()
    if remix_dict:
        transformer.remix(remix_dict)
    transformer.trim(time_start.total_seconds(), time_end.total_seconds())
    transformer.build_file(str(in_path), str(out_path))
    transformer.clear_effects()


def concat_audios(paths_in: list, path_out: Path) -> None:
    # Concatenate audio files at `paths_in` and write to `path_out`.
    combiner = Combiner()
    combiner.input_format = None
    combiner.convert(16000)
    paths_in_str = [str(path) for path in paths_in]
    path_out_str = str(path_out)
    combiner.build(paths_in_str, path_out_str, "concatenate")
    combiner.clear_effects()
