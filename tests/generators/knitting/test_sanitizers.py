import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Measure
from qiskit.quantum_info import Operator
from qiskit.circuit import Parameter
from generators.knitting.sanitizers import (
    RemoveMeasurementsSanitizer,
    RemoveMidCircuitMeasurementsSanitizer,
    AssignRandomParamsSanitizer,
    DropConditionedOperationsSanitizer
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


def test_assign_random_params():
    """
    Test that AssignRandomParamsSanitizer assigns random values to all unbound parameters.
    """
    # Create a quantum circuit with unbound parameters
    theta = Parameter('θ')
    phi = Parameter('φ')
    qc = QuantumCircuit(2)
    qc.rx(theta, 0)
    qc.ry(phi, 1)
    # gate with two parameters
    qc.u(theta, phi, 0, 0)

    # Apply the sanitizer
    sanitizer = AssignRandomParamsSanitizer()
    sanitized_qc = sanitizer.sanitize(qc)

    print(f"Original circuit:\n{qc}")
    print(f"Sanitized circuit:\n{sanitized_qc}")

    # Check that all parameters are bound
    assert not sanitized_qc.parameters, "There are still unbound parameters in the circuit"


def test_assign_random_params_no_unbound():
    """
    Test that AssignRandomParamsSanitizer does not alter a circuit with no unbound parameters.
    """
    # Create a quantum circuit with no unbound parameters
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    # Apply the sanitizer
    sanitizer = AssignRandomParamsSanitizer()
    sanitized_qc = sanitizer.sanitize(qc)

    print(f"Original circuit:\n{qc}")
    print(f"Sanitized circuit:\n{sanitized_qc}")
    viz_circuit = qc.draw(output='text')
    viz_sanitized = sanitized_qc.draw(output='text')

    # Check that the circuit remains unchanged
    assert f">{viz_circuit}<" == f">{viz_sanitized}<", "The circuit was altered despite having no unbound parameters"


def test_drop_conditioned_operations():
    """
    Test that DropConditionedOperationsSanitizer removes all conditioned operations from the circuit.
    """
    # Create a quantum circuit with conditioned operations
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.h(0).c_if(qc.cregs[0], 1)
    qc.cx(0, 1).c_if(qc.cregs[0], 1)
    qc.measure_all()

    # Apply the sanitizer
    sanitizer = DropConditionedOperationsSanitizer()
    sanitized_qc = sanitizer.sanitize(qc)

    print(f"Original circuit:\n{qc}")
    print(f"Sanitized circuit:\n{sanitized_qc}")

    # Check that all conditioned operations are removed
    for instruction in sanitized_qc.data:
        assert not instruction.operation.condition, "Circuit still has conditioned operations after sanitization"


def test_drop_conditioned_operations_no_condition():
    """
    Test that DropConditionedOperationsSanitizer does not alter a circuit with no conditioned operations.
    """
    # Create a quantum circuit with no conditioned operations
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Apply the sanitizer
    sanitizer = DropConditionedOperationsSanitizer()
    sanitized_qc = sanitizer.sanitize(qc)

    print(f"Original circuit:\n{qc}")
    print(f"Sanitized circuit:\n{sanitized_qc}")
    viz_circuit = qc.draw(output='text')
    viz_sanitized = sanitized_qc.draw(output='text')

    # Check that the circuit remains unchanged
    assert f">{viz_circuit}<" == f">{viz_sanitized}<", "The circuit was altered despite having no conditioned operations"
