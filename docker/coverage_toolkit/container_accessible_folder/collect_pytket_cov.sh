#!/bin/bash

# Script Name: collect_pytket_cov.sh
# Purpose: Collect and generate coverage report for pytket.
# Usage: ./collect_pytket_cov.sh <folder-path-or-filepath>
# Dependencies: gcovr

# Function to print usage instructions
usage() {
    echo "Usage: $0 <folder-path-or-filepath>"
    echo "       Argument can be either a direct folder path or a file containing the folder path"
    exit 1
}

# Function to copy the coverage report to the specified folder
copy_coverage_report() {
    local folder="$1"
    echo "Copying coverage report to the specified folder..."
    cp /home/regularuser/tket/cpp_coverage.xml "$folder"
    echo "Coverage report copied to $folder"
}

# Function to get the folder path
get_folder_path() {
    local input="$1"
    local folder

    if [[ -d "$input" ]]; then
        # Input is a directory
        folder="$input"
    elif [[ -f "$input" ]]; then
        # Input is a file, read the folder path from it
        folder=$(cat "$input")
    else
        echo "Error: Input is neither a valid folder nor a file"
        exit 1
    fi

    echo "$folder"
}

# Main script execution
main() {
    # Get the path argument
    local path_arg="${1:-}"

    # Check if the path argument is provided
    if [[ -z "$path_arg" ]]; then
        usage
    fi

    # Get the folder path
    local folder
    folder=$(get_folder_path "$path_arg")

    echo "Starting coverage collection..."

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