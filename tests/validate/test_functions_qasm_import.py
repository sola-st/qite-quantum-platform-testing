
import pytest
from validate.functions_qasm_import import import_from_qasm_with_qiskit
from validate.functions_qasm_import import import_from_qasm_with_pytket
from validate.functions_qasm_import import import_from_qasm_with_pennylane
from validate.functions_qasm_import import import_from_qasm_with_bqskit
import pennylane as qml


@pytest.fixture
def simple_qasm_str():
    return """OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
h q[0];
"""


def test_import_from_qasm_with_qiskit_simple_circuit(
        tmp_path, simple_qasm_str):
    """
    Test that import_from_qasm_with_qiskit can import a simple QASM file and return a circuit.
    """
    qasm_file = tmp_path / "simple_test.qasm"
    qasm_file.write_text(simple_qasm_str)
    circuit = import_from_qasm_with_qiskit(str(qasm_file))
    assert circuit.num_qubits == 1
    assert circuit.depth() >= 1


def test_import_from_qasm_with_pytket_simple_circuit(
        tmp_path, simple_qasm_str):
    """
    Test that import_from_qasm_with_pytket can import a simple QASM file and return a circuit.
    """
    qasm_file = tmp_path / "simple_test_pytket.qasm"
    qasm_file.write_text(simple_qasm_str)
    circuit = import_from_qasm_with_pytket(str(qasm_file))
    assert circuit.n_qubits == 1
    assert circuit.n_gates >= 1


def test_import_from_qasm_with_pennylane_simple_circuit(
        tmp_path, simple_qasm_str):
    """
    Test that import_from_qasm_with_pennylane can import a simple QASM file and return a circuit.
    """
    from pennylane.devices.default_qubit import DefaultQubit
    qasm_file = tmp_path / "simple_test_pennylane.qasm"
    qasm_file.write_text(simple_qasm_str)
    circuit = import_from_qasm_with_pennylane(str(qasm_file))
    qnode_circuit = qml.QNode(circuit, DefaultQubit(wires=1))
    circ_specs = qml.specs(qnode_circuit)()
    assert circ_specs['resources'].num_gates >= 1


def test_import_from_qasm_with_bqskit_simple_circuit(
        tmp_path, simple_qasm_str):
    """
    Test that import_from_qasm_with_bqskit can import a simple QASM file and return a circuit.
    """
    qasm_file = tmp_path / "simple_test_bqskit.qasm"
    qasm_file.write_text(simple_qasm_str)
    circuit = import_from_qasm_with_bqskit(str(qasm_file))
    assert circuit.num_qudits == 1
    assert circuit.num_operations >= 1
