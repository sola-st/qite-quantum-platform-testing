#!/bin/bash

# Script Name: collect_qiskit_cov.sh
# Purpose: Aggregate and export Qiskit coverage data, then copy the result to a specified folder.
# Usage: ./collect_qiskit_cov.sh <filepath-or-folder-path>
# Dependencies: llvm-profdata, llvm-cov, lcov_cobertura

# Function to display usage information
usage() {
    echo "Usage: $0 <filepath-or-folder-path>"
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
    # Get the path argument
    local path="${1:-}"

    # Check if the path is provided
    if [[ -z "$path" ]]; then
        usage
    fi

    # Determine if the path is a file or directory and get the folder path
    local folder
    if [ -f "$path" ]; then
        folder=$(cat "$path")
    elif [ -d "$path" ]; then
        folder="$path"
    else
        echo "Error: Provided path is neither a valid file nor a directory"
        exit 1
    fi

    # check if there are any profraw files
    if [ -z "$(compgen -G "/home/regularuser/databank/qiskit-*.profraw")" ]; then
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
