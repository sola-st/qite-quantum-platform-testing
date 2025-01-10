import pytest
import docker
from aiexchange.tools.docker_tools import get_grep_output_in_docker


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
