#!/bin/bash

# Script Name: collect_coverage_rust.sh
# Purpose: Collect and copy Rust coverage data to the host.
# Usage: ./collect_coverage_rust.sh
# Dependencies: llvm-profdata, llvm-cov, lcov_cobertura

set -euo pipefail

# Function to collect coverage data from Rust
collect_coverage() {
    echo "Collecting coverage data..."
    llvm-profdata merge -sparse qiskit-*.profraw -o my_program.profdata
    llvm-cov export -Xdemangler=rustfilt target/debug/libqiskit_pyext.so --instr-profile=my_program.profdata --format=lcov --ignore-filename-regex='^(?!crates).*$' > coverage.lcov
    lcov_cobertura -e '^(?!crates).*$' coverage.lcov -o rust_coverage.xml
    copy_coverage_to_host
}

# Function to copy the coverage data to the host
copy_coverage_to_host() {
    echo "Copying coverage data to host..."
    local latest_subfolder
    latest_subfolder=$(ls -d /home/regularuser/qiskit/program_bank/v040/*/ | sort | tail -n 1)
    cp rust_coverage.xml "$latest_subfolder"
}

# Automatically run the collect_coverage function
collect_coverage
