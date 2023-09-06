import argparse
import datetime
from itertools import product
from pathlib import Path

import pandas as pd
import shared
from invoke_reaper import invoke_reaper
from tqdm.contrib.concurrent import process_map
from utils.dirs import make_dirs_in_path_if_not_exist
from utils.sox import concatenate_audios


def main() -> None:
    dir_this_file = Path(__file__).parent.resolve()

    parser = argparse.ArgumentParser(
        description="Prepare DRAL release short fragments data for MATLAB feature "
        "computation: (1) drop fragments with short duration, (2) concatenate "
        "fragments from each conversation track into a new audio, (3) create a new "
        "metadata file, and (4) estimate concatenated audio pitch with REAPER.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--dir_input",
        help="Path to DRAL release.",
        default=dir_this_file.joinpath("release"),
    )
    parser.add_argument(
        "-o",
        "--dir_output",
        help="Directory to write output files to.",
        default=dir_this_file.joinpath("release"),
    )
    args = parser.parse_args()

    path_input_metadata = args.dir_input.joinpath("fragments-short-complete.csv")
    dir_output = Path(args.dir_output)

    path_output_metadata = dir_output.joinpath("fragments-short-matlab.csv")
    dir_output_concat_audios = dir_output.joinpath("fragments-short-concatenated")
    dir_output_concat_audios_pitch = dir_output_concat_audios.joinpath("f0reaper")

    if path_output_metadata.exists():
        print(f"Stopped. Output already exists: {path_output_metadata}")
        return
    if dir_output_concat_audios.exists():
        print(f"Stopped. Output already exists: {dir_output_concat_audios}")
        return

    # TODO Possible duplicate code from data.py.
    df_frags = pd.read_csv(path_input_metadata, index_col="id")
    df_frags["duration"] = df_frags["duration"].apply(pd.to_timedelta)

    df_frags = drop_fragments_with_short_duration(df_frags)

    df_frags["audio_path"] = df_frags["audio_path"].apply(
        lambda p: Path(args.dir_input).joinpath(p)
    )

    df_frags = concatenate_fragment_audios(df_frags, dir_output_concat_audios)

    print("Estimating pitch with REAPER...")
    make_dirs_in_path_if_not_exist(dir_output_concat_audios_pitch)
    paths_reaper_inputs = pd.unique(df_frags["concat_audio_path"])
    paths_reaper_outputs = [
        dir_output_concat_audios_pitch.joinpath(p.with_suffix(".txt").name)
        for p in paths_reaper_inputs
    ]
    process_map(
        invoke_reaper,
        paths_reaper_inputs,
        paths_reaper_outputs,
        total=len(paths_reaper_inputs),
    )

    # Write only the columns expected by MATLAB scripts, in order.
    df_frags["audio_path"] = df_frags["audio_path"].apply(
        lambda p: p.relative_to(dir_output)
    )
    df_frags["concat_audio_path"] = df_frags["concat_audio_path"].apply(
        lambda p: p.relative_to(dir_output)
    )
    df_frags.to_csv(
        path_output_metadata,
        columns=[
            "conv_id",
            "lang_code",
            "original_or_reenacted",
            "time_start_rel",
            "time_end_rel",
            "duration",
            "audio_path",
            "concat_audio_path",
            "trans_id",
            "trans_lang_code",
            "participant_id_unique",
        ],
    )

    print(f"Done. Output written to: {dir_output}")


def drop_fragments_with_short_duration(df_frags: pd.DataFrame) -> pd.DataFrame:
    min_duration = datetime.timedelta(milliseconds=500)
    has_tiny_duration = df_frags["duration"] < min_duration
    idx_tiny_duration = df_frags[has_tiny_duration].index
    idx_tiny_duration_trans = df_frags[
        df_frags["trans_id"].isin(idx_tiny_duration)
    ].index
    idx_to_drop = idx_tiny_duration.union(idx_tiny_duration_trans)
    n_to_drop = len(idx_to_drop)
    print(
        f"Number of utterances dropped due to short duration (including translation): {n_to_drop}"
    )
    df_frags.drop(idx_to_drop, inplace=True)
    return df_frags


def concatenate_fragment_audios(
    df_frags: pd.DataFrame, dir_output: Path
) -> pd.DataFrame:
    # New columns to be added.
    col_concat_audio_path = "concat_audio_path"
    col_time_start_relative = "time_start_rel"
    col_time_end_relative = "time_end_rel"

    make_dirs_in_path_if_not_exist(dir_output)

    # Each item in this list will be a tuple of: (list of input fragment audio paths,
    # output concatenated audio path).
    paths_inputs_and_output = []

    conv_ids_unique = df_frags["conv_id"].unique()
    short_tiers = [shared.MARKUP_TIER_LEFT, shared.MARKUP_TIER_RIGHT]

    # For each combination of conversation ID and tier (left or right track of stereo
    # audio).
    problem_track_tripped = False  # Just for nicer printing.
    for conv_id, tier in list(product(conv_ids_unique, short_tiers)):
        # Get indices of fragments belonging to this conversation and tier.
        is_in_conv = df_frags["conv_id"] == conv_id
        is_in_tier = df_frags["tier_name"] == tier.name
        idx_to_concat = df_frags.index[is_in_conv & is_in_tier]

        n_frags_to_concat = idx_to_concat.size
        if n_frags_to_concat <= 1:
            if problem_track_tripped is False:
                print("The following conversation tracks were ignored:")
                problem_track_tripped = True
            print(
                f"\t- Conversation {conv_id}, tier {tier.name} with {n_frags_to_concat} fragments"
            )
            continue

        paths_input_audio = df_frags.loc[idx_to_concat, "audio_path"].tolist()
        path_output_audio = dir_output.joinpath(f"{conv_id}{tier.track_side_code}.wav")

        # Append input audio paths and output audio path tuple to list.
        paths_inputs_and_output.append((paths_input_audio, path_output_audio))

        # Insert: concatenated audio fragment relative end time.
        df_frags.loc[idx_to_concat, col_time_end_relative] = df_frags.loc[
            idx_to_concat, "duration"
        ].cumsum()

        # Insert: concatenated audio fragment relative start time.
        df_frags.loc[idx_to_concat, col_time_start_relative] = (
            df_frags.loc[idx_to_concat, col_time_end_relative]
            - df_frags.loc[idx_to_concat, "duration"]
        )

        # Insert: path to output concatenated audio.
        df_frags.loc[idx_to_concat, col_concat_audio_path] = path_output_audio

    print("Concatenating short fragment audios...")
    process_map(
        concatenate_audios,
        list(zip(*paths_inputs_and_output))[0],  # Input fragment audio paths.
        list(zip(*paths_inputs_and_output))[1],  # Output concatenated audio paths.
        total=len(paths_inputs_and_output),
    )

    # Drop fragments missing concatenation.
    idx_lacks_concat = df_frags[df_frags["concat_audio_path"].isna()].index
    idx_lacks_concat_trans = df_frags[
        df_frags.index.isin(df_frags.loc[idx_lacks_concat, "trans_id"])
    ].index
    idx_to_drop = idx_lacks_concat.union(idx_lacks_concat_trans)
    df_frags.drop(idx_to_drop, inplace=True)
    print(f"{idx_to_drop.size} fragments are missing concatenation and were dropped.")

    # TODO If audio is from synthesis, add noise.This avoids the pitch detection (later
    # in MATLAB) returning NaNs.
    # process_map(
    #     add_noise,
    #     list(zip(*paths_inputs_and_output))[1],  # Output concatenated audio paths.
    #     total=len(paths_inputs_and_output),
    # )

    # Return the augmented DataFrame.
    return df_frags


if __name__ == "__main__":
    main()
