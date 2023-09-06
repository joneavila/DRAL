import subprocess
from pathlib import Path


def invoke_reaper(input_file: Path, output_file: Path):
    # This might require the right permissions. Use chmod.

    if input_file.suffix != ".wav":
        raise ValueError(f"Input file must be a WAV file: {input_file}")

    if output_file.suffix != ".txt":
        raise ValueError(f"Output file must be a TXT file: {output_file}")

    completed_process = subprocess.run(
        [
            "reaper",
            "-i",
            str(input_file),
            "-f",
            str(output_file),
            "-m",
            "80",
            "-x",
            "500",
            "-a",
            "-e",
            "0.01",
        ],
        capture_output=True,
    )
    if completed_process.returncode != 0:
        print(
            f"REAPER failed: {completed_process.returncode}.\n\tArguments: "
            f"{completed_process.args}\n\tError: {completed_process.stderr}"
        )
