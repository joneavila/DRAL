#!/bin/bash

# This script estimates pitch for all audios in an input directory by calling REAPER
# commands and stores its output as text files in a subdirectory in the same input
# directory. See usage message below.

# REAPER (Robust Epoch And Pitch EstimatoR) GitHub repository:
# https://github.com/google/REAPER

# This script is modified from
# https://github.com/nigelgward/istyles/blob/76ae51e727c1ae93b1db0797c496914caca285ae/src/sph-to-wav.bash
# with the following changes:
#   - Remove split audio tracks with sox. This is handled by make_DRAL_release.py.
#   - Add command line argument for input directory.
#   - Assume reaper is in PATH environment variable.

# This script assumes REAPER is in your PATH environment variable. Download and build
# REAPER from the GitHub repository above. Instructions for adding reaper to your PATH
# environment variable depends on your operating system and shell.
# To add REAPER to PATH on MacOS with Z shell (Zsh), add the following line to
# ~/.zprofile,
#   export PATH="<directory containing reaper>:$PATH"
# For example,
#   export PATH="/Users/jon/REAPER/build:$PATH"
# To add REAPER to PATH on Windows, try this guide:
# https://windowsloop.com/how-to-add-to-windows-path/

# If the number of command line arguments (`$#`) is not equal (`-ne`) to 1, then
# print the name of the script (`$0`) and a usage message and exit.
if [ $# -ne 1 ]; then
    name=$0
    echo "Usage: $name INPUT_DIR"
    echo "Read .wav files in INPUT_DIR and write F0 (pitch) as .txt to \
<INPUT_DIR>/../f0reaper."
    exit 1
fi

# Make output directory (in case it does not exist). The output directory will be named
# "f0reaper" and will be created as a subdirectory in the input directory. This is the
# expected location by lookupOrComputePitchModified.m.
output_dir="$1/f0reaper"
mkdir -p "$output_dir"

# For each .wav file in INPUT_DIR.
for input_file in "$1"/*.wav
do

    # Remove prefix ending with the last slash (`/`) and the suffix `.wav` from the
    # input filename. Output files will have the same base name.
    input_file_basename=$(basename "$input_file" .wav)

    # Print the input file basename, useful for debugging.
    printf "$input_file_basename\n"

    # Execute REAPER with the following flags:
    #   `-i "${input_file}"` is the input file
    #   `-f "$output_dir/$input_file_basename.txt"` is the output file
    #   `-m 80` is the minimum F0 to look for
    #   `-x 500` is the maximum F0 to look for
    #   `-a` saves the output in ASCII mode
    #   `-e 0.01` is the output interval for F0 (10ms to match Midlevel Toolkit's frame
    #       width)
    reaper -i "${input_file}" -f "$output_dir/$input_file_basename.txt" -m 80 -x 500 -a -e 0.01

done
