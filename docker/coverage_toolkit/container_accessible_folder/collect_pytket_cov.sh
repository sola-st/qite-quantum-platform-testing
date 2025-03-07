#!/bin/bash

# Script Name: collect_pytket_cov.sh
# Purpose: Collect and generate coverage report for pytket.
# Usage: ./collect_pytket_cov.sh <config-folder-name> <filepath-with-folder-path>
# Dependencies: gcovr


# Function to print usage instructions
usage() {
    echo "Usage: $0 <config-folder-name> <filepath-with-folder-path>"
    exit 1
}


# Function to copy the coverage report to the specified folder
copy_coverage_report() {
    local folder="$1"
    echo "Copying coverage report to the specified folder..."
    cp /home/regularuser/tket/cpp_coverage.xml "$folder"
    echo "Coverage report copied to $folder"
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

    echo "Starting coverage collection for config folder: $config_folder_name"

    echo "Searching for GCDA files..."
    gcda_path=$(find /home/regularuser/.conan2/p/b/tket* -name "*.gcda" | grep -o '.*/Debug' | head -n 1)
    if [[ -z "$gcda_path" ]]; then
        echo "Error: No GCDA files found."
        exit 1
    fi
    echo "GCDA path found: $gcda_path"

    echo "Creating coverage report..."
    gcovr --print-summary --xml-pretty --xml -r "${gcda_path}/../../src/" \
          --exclude-lines-by-pattern='.*\bTKET_ASSERT\(.*\);' \
          --object-directory="${gcda_path}/CMakeFiles/tket.dir/src" \
          -o /home/regularuser/tket/cpp_coverage.xml --decisions
    echo "Coverage report created at /home/regularuser/tket/cpp_coverage.xml"

    # Copy the cpp_coverage.xml to the specified folder
    copy_coverage_report "$folder"

    echo "Coverage collection completed successfully."
}

# Run the main function
main "$@"