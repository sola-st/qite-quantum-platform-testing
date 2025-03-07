#!/bin/bash

# Script Name: collect_qiskit_cov.sh
# Purpose: Aggregate and export Qiskit coverage data, then copy the result to a specified folder.
# Usage: ./collect_qiskit_cov.sh <config-folder-name> <filepath-with-folder-path>
# Dependencies: llvm-profdata, llvm-cov, lcov_cobertura

# set -euo pipefail

# Function to display usage information
usage() {
    echo "Usage: $0 <config-folder-name> <filepath-with-folder-path>"
    exit 1
}

# Function to aggregate coverage data
aggregate_coverage_data() {
    cd /home/regularuser/databank/
    /usr/bin/llvm-profdata-16 merge -sparse qiskit-*.profraw -o my_program.profdata
    cp my_program.profdata /home/regularuser/qiskit
    cd /home/regularuser/qiskit
    /usr/bin/llvm-cov-16 export -Xdemangler=rustfilt target/debug/libqiskit_pyext.so --instr-profile=my_program.profdata --format=lcov --ignore-filename-regex='^(?!crates).*$' > coverage.lcov
    python -m lcov_cobertura -e '^(?!crates).*$' coverage.lcov -o rust_coverage.xml
}

# Function to copy the coverage report to the specified folder
copy_coverage_report() {
    local folder="$1"
    cp rust_coverage.xml "/home/regularuser/databank/$folder"
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

    # check if there is any profraw file
    if [ ! -f /home/regularuser/databank/qiskit-*.profraw ]; then
        echo "Error: No profraw files found. Skipping coverage collection RUST."
        exit 0
    fi

    # Aggregate the coverage data
    aggregate_coverage_data

    # Copy the rust_coverage.xml to the specified folder
    copy_coverage_report "$folder"
}

# Execute the main function
main "$@"

