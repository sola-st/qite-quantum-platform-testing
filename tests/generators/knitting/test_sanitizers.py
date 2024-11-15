import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Measure
from qiskit.quantum_info import Operator
from generators.knitting.sanitizers import (
    RemoveMeasurementsSanitizer,
    RemoveMidCircuitMeasurementsSanitizer
)


def test_remove_measurements():
    """
    Test that RemoveMeasurementSanitizer removes all measurements from the circuit.
    """
    # Create a quantum circuit with measurements
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Apply the sanitizer
    sanitizer = RemoveMeasurementsSanitizer()
    sanitized_qc = sanitizer.sanitize(qc)

    print(f"Original circuit:\n{qc}")
    print(f"Sanitized circuit:\n{sanitized_qc}")

    # Check that all measurements are removed
    for instruction in sanitized_qc.data:
        assert instruction.operation.name != 'measure'


def test_remove_measurements_subcircuit():
    """
    Test that RemoveMeasurementSanitizer removes all measurements from the circuit,
    including those in subcircuits.
    """
    # Create a quantum circuit with measurements in a subcircuit
    sub_qc = QuantumCircuit(2, 2, name='subcircuit')
    sub_qc.h(0)
    sub_qc.cx(0, 1)
    sub_qc.ecr(0, 1)
    sub_qc.measure([0, 1], [0, 1])

    qc = QuantumCircuit(2, 2)
    qc.append(sub_qc.to_instruction(), [0, 1], [0, 1])

    # Apply the sanitizer
    sanitizer = RemoveMeasurementsSanitizer()
    sanitized_qc = sanitizer.sanitize(qc)

    print(f"Original circuit with subcircuit:\n{qc}")
    print(f"Sanitized circuit with subcircuit:\n{sanitized_qc}")

    # Check that all measurements are removed
    check_for_no_measurement(sanitized_qc)


def check_for_no_measurement(qc: QuantumCircuit, decomposition_level: int = 5):
    """Check that the circuit has no measurements."""
    for _ in range(decomposition_level):
        qc = qc.decompose()
    for instruction in qc.data:
        if isinstance(instruction.operation, QuantumCircuit):
            if decomposition_level > 0:
                check_for_no_measurement(
                    instruction.operation, decomposition_level - 1)
        else:
            assert not isinstance(
                instruction.operation, Measure), "Circuit still has measurements after sanitization"


def is_unitary_if_removing_final_measurements(qc: QuantumCircuit):
    """Check that the circuit is unitary if removing final measurements."""
    qc.remove_final_measurements(inplace=True)
    print(f"Sanitized circuit without final measurements:\n{qc}")
    Operator.from_circuit(qc)


def test_remove_mid_circuit_measurements():
    """
    Test that RemoveMidCircuitMeasurementsSanitizer removes all mid-circuit measurements from the circuit.
    """
    # Create a quantum circuit with measurements in the middle
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.measure(0, 0)
    qc.cx(0, 1)
    qc.measure(1, 1)

    # Apply the sanitizer
    sanitizer = RemoveMidCircuitMeasurementsSanitizer()
    sanitized_qc = sanitizer.sanitize(qc)

    print(f"Original circuit:\n{qc}")
    print(f"Sanitized circuit:\n{sanitized_qc}")

    # Check that all mid-circuit measurements are removed
    is_unitary_if_removing_final_measurements(sanitized_qc)
