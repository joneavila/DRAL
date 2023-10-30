#!/bin/bash
# This script downsamples all 44.1 kHz WAV files in a directory to 16 kHz.

# Function to downsample file and overwrite original file
downsample_file() {
  local file="$1"
  echo "Processing $file"
  local temp_file="temp_$(basename "$file")"
  sox "$file" -r 16000 "$temp_file"
  mv "$temp_file" "$file"
}

# Function to downsample a directory
process_directory() {
  local dir="$1"
  local files=$(find "$dir" -type f -name "*.wav")
  for file in $files; do
    # Downsample if file is a 44.1 kHz WAV
    local rate=$(soxi -r "$file")
    if [ "$rate" -eq 44100 ]; then
      downsample_file "$file"
    fi
  done
}

if [ -z "$1" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi
dir_to_process="$1"
process_directory "$dir_to_process"
