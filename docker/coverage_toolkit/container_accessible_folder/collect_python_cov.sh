#!/bin/bash

# Script Name: collect_python_cov.sh
# Purpose: Aggregate and export Python coverage data, then copy the result to a specified folder.
# Usage: ./collect_python_cov.sh <config-folder-name> <filepath-with-folder-path>
# Dependencies: coverage

# set -euo pipefail

# Function to display usage information
usage() {
    echo "Usage: $0 <config-folder-name> <filepath-with-folder-path>"
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

# Main script execution
main() {
    # Get the config folder name and the file path from the arguments
    local config_folder_name="${1:-}"
    local filepath_with_folder_path="${2:-}"

    # Check if the config folder name and file path are provided
    if [[ -z "$config_folder_name" || -z "$filepath_with_folder_path" ]]; then
        usage
    fi

    # Read the folder path from the file
    local folder
    folder=$(cat "$filepath_with_folder_path")

    # print current folder and folder
    echo "Current folder: $(pwd)"
    echo "Specified folder: $folder"
    # Aggregate the coverage data
    aggregate_coverage_data "$folder"
}

# Execute the main function
main "$@"