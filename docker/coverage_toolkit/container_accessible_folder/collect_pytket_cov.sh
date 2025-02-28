#!/bin/bash

# Script Name: collect_pytket_cov.sh
# Purpose: Collect and generate coverage report for pytket.
# Usage: ./collect_pytket_cov.sh <config-folder-name>
# Dependencies: gcovr


# Function to print usage instructions
usage() {
    echo "Usage: $0 <config-folder-name>"
    exit 1
}


# Function to copy the coverage report to the latest subfolder
copy_coverage_report() {
    local config_folder_name="$1"
    echo "Copying coverage report to the latest subfolder..."
    local latest_subfolder
    latest_subfolder=$(ls -d /home/regularuser/databank/program_bank/"${config_folder_name}"/*/ | sort | tail -n 1)
    if [[ -z "$latest_subfolder" ]]; then
        echo "Error: No subfolders found in /home/regularuser/databank/program_bank/${config_folder_name}/"
        exit 1
    fi
    cp /home/regularuser/tket/cpp_coverage.xml "$latest_subfolder"
    echo "Coverage report copied to $latest_subfolder"
}

# Main script execution
main() {
    # Get the config folder name from the first argument
    local config_folder_name="${1:-}"

    # Check if the config folder name is provided
    if [[ -z "$config_folder_name" ]]; then
        usage
    fi

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

    # Copy the cpp_coverage.xml to the host
    copy_coverage_report "$config_folder_name"

    echo "Coverage collection completed successfully."
}

# Run the main function
main "$@"