#!/bin/bash

# Script Name: collect_qiskit_cov.sh
# Purpose: Aggregate and export Qiskit coverage data, then copy the result to a specified folder.
# Usage: ./collect_qiskit_cov.sh <config-folder-name>
# Dependencies: llvm-profdata, llvm-cov, lcov_cobertura

# set -euo pipefail

# Function to display usage information
usage() {
    echo "Usage: $0 <config-folder-name>"
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

# Function to copy the coverage report to the latest subfolder
copy_coverage_report() {
    local config_folder_name="$1"
    local latest_subfolder

    latest_subfolder=$(ls -d /home/regularuser/databank/program_bank/"${config_folder_name}"/*/ | sort | tail -n 1)
    cp rust_coverage.xml "$latest_subfolder"
}

# Main script execution
main() {
    # Get the config folder name from the first argument
    local config_folder_name="${1:-}"

    # Check if the config folder name is provided
    if [[ -z "$config_folder_name" ]]; then
        usage
    fi

    # Aggregate the coverage data
    aggregate_coverage_data

    # Copy the rust_coverage.xml to the host
    copy_coverage_report "$config_folder_name"
}

# Execute the main function
main "$@"

