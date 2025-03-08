#!/bin/bash

# Script Name: collect_python_cov.sh
# Purpose: Aggregate and export Python coverage data, then copy the result to a specified folder.
# Usage: ./collect_python_cov.sh <folder-path-or-filepath>
# Dependencies: coverage

# Function to display usage information
usage() {
    echo "Usage: $0 <folder-path-or-filepath>"
    exit 1
}

# Function to aggregate coverage data
aggregate_coverage_data() {
    local folder="$1"
    cd /home/regularuser/databank
    coverage combine --rcfile="${folder}/coverage.rc"
    echo "location of coverage data: ${folder}/coverage.rc"
    coverage xml -o ${folder}/coverage.xml --rcfile="${folder}/coverage.rc"
}

# Function to get folder path
get_folder_path() {
    local input="$1"
    local folder

    if [[ -f "$input" ]]; then
        # If input is a file, read the folder path from it
        folder=$(cat "$input")
    elif [[ -d "$input" ]]; then
        # If input is a directory, use it directly
        folder="$input"
    else
        echo "Error: Input must be either a valid file containing a folder path or a valid folder path"
        exit 1
    fi

    echo "$folder"
}

# Main script execution
main() {
    # Get the input path from the arguments
    local input_path="${1:-}"

    # Check if the input path is provided
    if [[ -z "$input_path" ]]; then
        usage
    fi

    # Get the folder path
    local folder
    folder=$(get_folder_path "$input_path")

    # print current folder and folder
    echo "Current folder: $(pwd)"
    echo "Specified folder: $folder"

    # Aggregate the coverage data
    aggregate_coverage_data "$folder"
}

# Execute the main function
main "$@"