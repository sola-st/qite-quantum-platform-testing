import pytest
import docker
from pathlib import Path
from aiexchange.tools.docker_tools import get_grep_output_in_docker
from aiexchange.tools.docker_tools import run_script_in_docker


def test_get_grep_output_in_docker_success():
    """
    Test that get_grep_output_in_docker returns the correct logs when the file exists.
    """

    result = get_grep_output_in_docker(
        image_name="qiskit_image_0.45.0",
        pattern="class QuantumCircuit:",
        file_dir="/usr/local/lib/python3.10/site-packages/qiskit",
        context_size=0,
        compress=True,
    )
    assert result.strip() == "qiskit/circuit/quantumcircuit.py:class QuantumCircuit:"


def test_get_grep_output_in_docker_regex_enabled():
    """
    Test that get_grep_output_in_docker returns the correct logs when regex is enabled.
    """

    result = get_grep_output_in_docker(
        image_name="qiskit_image_0.45.0",
        pattern="class Gaussian\\(",
        file_dir="/usr/local/lib/python3.10/site-packages/qiskit",
        context_size=0,
        regex_enabled=True,
        compress=True,
    )
    assert result.strip() == (
        "qiskit/pulse/library/parametric_pulses.py:class Gaussian(ParametricPulse):\n"
        "--\n"
        "qiskit/pulse/library/symbolic_pulses.py:class Gaussian(metaclass=_PulseType):"
    )


def test_get_grep_output_in_docker_file_not_found():
    """
    Test that get_grep_output_in_docker returns None when the file directory does not exist.
    """

    result = get_grep_output_in_docker(
        image_name="qiskit_image_0.45.0",
        pattern="class QuantumCircuit:",
        file_dir="/non/existent/directory",
        context_size=0,
        compress=False,
    )
    assert result == f"grep: /non/existent/directory: No such file or directory\n"


def test_get_grep_output_in_docker_no_match():
    """
    Test that get_grep_output_in_docker returns an empty string when no match is found.
    """

    result = get_grep_output_in_docker(
        image_name="qiskit_image_0.45.0",
        pattern="non_existent_pattern",
        file_dir="/usr/local/lib/python3.10/site-packages/qiskit",
        context_size=0,
        compress=True,
    )
    assert result.strip() == ""


def test_run_script_in_docker_success():
    """
    Test that run_script_in_docker runs the script successfully and returns the correct logs.
    """
    folder_current_file = Path(__file__).parent
    script_path = folder_current_file / "toy_script.py"
    image_name = "python:3.10-slim"
    options = {"name": "Alice"}

    result = run_script_in_docker(script_path, image_name, options)
    assert result.strip() == "Hello, Alice!"


def test_run_script_in_docker_with_output_path():
    """
    Test that run_script_in_docker runs the script successfully and writes the output to the specified file.
    """
    folder_current_file = Path(__file__).parent
    script_path = folder_current_file / "toy_script_write.py"
    output_path = folder_current_file / "greeting.txt"
    image_name = "python:3.10-slim"
    options = {"name": "Bob", "output_path": str(output_path)}

    result = run_script_in_docker(
        script_path, image_name, options, output_dir=str(output_path))
    assert result.strip() == "Hello, Bob!"

    with open(output_path, 'r') as file:
        content = file.read().strip()
    assert content == "Hello, Bob!"

    # Clean up
    output_path.unlink()
