from analysis_and_reporting.triage import extract_circuit_variable_name
import pytest


def test_extract_circuit_variable_name_qc():
    """Test that the function extracts 'qc' from the given file path."""
    program_path = "qiskit_circuit_5q_10g_7553_24d42f_76b26a_error_min_qc_qiskit.qasm"
    expected = "qc"
    assert extract_circuit_variable_name(program_path) == expected


def test_extract_circuit_variable_name_random_qc():
    """Test that the function extracts 'random_qc' from the given file path."""
    program_path = "qiskit_circuit_5q_10g_7553_24d42f_76b26a_error_min_random_qc_pytket.qasm"
    expected = "random_qc"
    assert extract_circuit_variable_name(program_path) == expected


def test_extract_circuit_variable_name_empty():
    """Test that the function returns an empty string if no variable name is found."""
    program_path = "qiskit_circuit_5q_10g_7553_24d42f_76b26a_error_min_.qasm"
    expected = ""
    assert extract_circuit_variable_name(program_path) == expected
