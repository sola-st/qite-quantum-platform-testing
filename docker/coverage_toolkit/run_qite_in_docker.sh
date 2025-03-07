#!/bin/bash
# Script Name: run.sh
# Purpose: Build and run a Docker container for Qiskit with Rust, and collect coverage data.

# Usage: ./run.sh -c <config_file>
# Dependencies: Docker, Python, LLVM, lcov, lcov_cobertura
# License: Your License Information

set -euo pipefail

CONFIG_FILE=""
INTERACTIVE_MODE=false

# Function to display help message
show_help() {
    echo "Usage: $0 -c <config_file> [--interactive]"
    echo ""
    echo "Options:"
    echo "  -c <config_file>  Path to the configuration file (e.g., config/v040.yaml)"
    echo "  --interactive     Run in interactive mode"
    echo "  -h                Show this help message"
}

parse_args() {
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            -c)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --interactive)
                INTERACTIVE_MODE=true
                shift
                ;;
            -h)
                show_help
                exit 0
                ;;
            *)
                echo "Invalid option: $1" 1>&2
                show_help
                exit 1
                ;;
        esac
    done

    if [ -z "$CONFIG_FILE" ]; then
        echo "Error: Configuration file is required."
        show_help
        exit 1
    fi

    CONFIG_NAME=$(basename "$CONFIG_FILE" .yaml)
}

# Function to check if the script is run from the main folder of the repo
check_main_folder() {
    if [[ ! -f "pyproject.toml" ]]; then
        echo "Error: pyproject.toml not found. Please run the script from the main folder of the repository."
        exit 1
    fi

    if ! grep -q 'name = "qite"' pyproject.toml; then
        echo "Error: pyproject.toml does not contain the expected project name 'qite'."
        exit 1
    fi
}

# Function to build the Docker image
build_docker() {
    echo "Building Docker image..."
    docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t quantum_compilers_from_source docker/coverage_toolkit
}

# Function to run the Docker container
run_docker() {
    echo "Running Docker container with QITE..."

    INTERACTIVE_FLAG_DOCKER=""
    if [ "$INTERACTIVE_MODE" = true ]; then
        INTERACTIVE_FLAG_DOCKER="-it"
    fi

    DOCKER_CMD="docker run --rm $INTERACTIVE_FLAG_DOCKER \
        -v \"$(pwd)/docker/coverage_toolkit/container_accessible_folder:/home/regularuser/host\" \
        -v \"$(pwd)/program_bank:/home/regularuser/databank/program_bank\" \
        -v \"$(pwd)/config:/home/regularuser/databank/config\" \
        -v \"$(pwd)/tests/e2e/config:/home/regularuser/databank/tests/e2e/config\" \
        -v \"$(pwd)/logs:/home/regularuser/databank/logs\" \
        -v \"$(pwd)/entry.py:/home/regularuser/databank/entry.py\" \
        -v \"$(pwd)/qite:/home/regularuser/app/qite\" \
        -v \"$(pwd)/pyproject.toml:/home/regularuser/app/pyproject.toml\" \
        quantum_compilers_from_source /bin/bash -i -c \"
            which python && \
            bash /home/regularuser/host/install_qite.sh && \
            cd /home/regularuser/databank && \
            python entry.py --config $CONFIG_FILE --continuous_fuzzing | tee /tmp/full_output.txt && \
            tail -n 1 /tmp/full_output.txt > /home/regularuser/databank/output_folder.txt && \
            rm /tmp/full_output.txt && \
            bash /home/regularuser/host/collect_qiskit_cov.sh $CONFIG_NAME /home/regularuser/databank/output_folder.txt && \
            bash /home/regularuser/host/collect_pytket_cov.sh $CONFIG_NAME /home/regularuser/databank/output_folder.txt && \
            bash /home/regularuser/host/collect_python_cov.sh $CONFIG_NAME /home/regularuser/databank/output_folder.txt && \
            python -m qite.compute_coverage --folder_path /home/regularuser/databank/output_folder.txt
        \""

    echo "$DOCKER_CMD"
    eval "$DOCKER_CMD"
    # add --continuous_fuzzing flag to the python entry command if needed
}

# Main script execution
main() {
    parse_args "$@"
    check_main_folder
    build_docker
    run_docker
}

main "$@"