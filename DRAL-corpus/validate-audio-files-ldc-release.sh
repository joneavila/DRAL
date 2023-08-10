#!/bin/bash

# A quick and dirty script to validate the audio files in the LDC release.
# (Recently I've been running low on disk space and this has caused some
# broken or missing files.)

process_csv() {

    csv_file="$1" # First arg: path to `fragments-short.csv` or `fragments-long.csv`
    dir_audio="$2" # Second arg: path to directory containing short or long fragment audio files

    if [ ! -f "$csv_file" ]; then
        echo "CSV file does not exist: $csv_file"
        return
    fi
    # Skip the header line (column names), then process each line
    tail -n +2 "$csv_file" | while IFS=',' read -r line
    do
        # Read the "id" column
        id=$(echo "$line" | cut -d ',' -f 1)

        # Infer the path to the FLAC file using the fragment's ID
        flac_file="${dir_audio}/${id}.flac"

        if [ ! -f "$flac_file" ]; then
            echo "FLAC file does not exist: $flac_file"
        else
            flac -t "$flac_file" --silent 2>&1 >/dev/null 
            if [ $? -ne 0 ]; then
                echo "FLAC file is not valid: $flac_file"
                exit 1
            fi
        fi
    done
}

# process_csv <path to /data/speech/metadata/fragments-short.csv> <path to /data/speech/fragments-short/>
# process_csv <path to /data/speech/metadata/fragments-long.csv> <path to /data/speech/fragments-long/>
# echo "Done."