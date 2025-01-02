import os
from math import pi

import pennylane as qml
import pytest
from pytket import Circuit as tkCircuit
from qiskit import QuantumCircuit
from bqskit.ir import Circuit as bqCircuit
from bqskit.ir.gates import U3Gate, HGate, RXGate, RZGate

from validate.functions_optimize import (
    optimize_with_pytket,
    optimize_with_qiskit,
    optimize_with_pennylane,
    optimize_with_bqskit,
)


@pytest.fixture
def simple_tk_circuit():
    circuit = tkCircuit(1)
    circuit.H(0)
    return circuit


@pytest.fixture
def simple_qiskit_circuit():
    circuit = QuantumCircuit(1)
    circuit.h(0)
    return circuit


@pytest.fixture
def simple_bqskit_circuit():
    circuit = bqCircuit(3)
    circuit.append_gate(HGate(), [0])
    circuit.append_gate(HGate(), [0])
    circuit.append_gate(HGate(), [0])
    circuit.append_gate(RXGate(pi/2), [1])
    circuit.append_gate(RXGate(pi/2), [1])
    circuit.append_gate(RZGate(pi), [2])
    circuit.append_gate(RZGate(pi), [2])
    return circuit


@pytest.fixture
def simple_pennylane_circuit():

    def base_circuit():
        qml.Hadamard(wires=0)
        qml.PauliY(wires=1)
        qml.PauliZ(wires=2)

    return base_circuit


@pytest.fixture
def inefficient_pennylane_circuit():

    def inefficient_circuit():
        qml.RZ(0.1, wires=0)
        qml.Hadamard(wires=0)
        qml.Hadamard(wires=0)
        qml.RX(0.3, wires=1)
        qml.Hadamard(wires=0)
        qml.RX(0.4, wires=1)

    return inefficient_circuit


def test_optimize_with_pytket_simple_circuit(tmp_path, simple_tk_circuit):
    """
    Test that optimize_with_pytket can optimize a simple pytket circuit and export it as QASM.
    """
    var_name = "simple_test"
    os.chdir(tmp_path)
    optimize_with_pytket(simple_tk_circuit, var_name, output_dir=tmp_path)
    all_files = os.listdir(tmp_path)
    for file in all_files:
        print(file)
        filepath = os.path.join(tmp_path, file)
        content = open(filepath, 'r').read().strip()
        assert content.startswith("OPENQASM 2.0;")


def test_optimize_with_qiskit_simple_circuit(tmp_path, simple_qiskit_circuit):
    """
    Test that optimize_with_qiskit can optimize a simple Qiskit circuit and export it as QASM.
    """
    var_name = "simple_test"
    optimize_with_qiskit(simple_qiskit_circuit, var_name, output_dir=tmp_path)
    all_files = os.listdir(tmp_path)
    for file in all_files:
        print(file)
        filepath = os.path.join(tmp_path, file)
        content = open(filepath, 'r').read().strip()
        assert content.startswith("OPENQASM 2.0;")


def get_specs(circuit_fn):
    """Get the specs of a PennyLane circuit.

    NOTE: this works only if the circuit function takes no arguments.
    """
    dev = qml.device("default.qubit", wires=128)

    @qml.qnode(dev)
    def scaffold_for_qnode(subcircuit):
        subcircuit()

    specs = qml.specs(scaffold_for_qnode)(
        circuit_fn)
    return specs


def get_number_of_qubits(circuit_fn) -> int:
    """Get the number of qubits in a PennyLane circuit."""
    specs = get_specs(circuit_fn)
    return specs["resources"].num_wires


def test_join_circuits_with_pennylane(tmp_path, simple_pennylane_circuit):
    """
    Test that join_circuits can combine a simple PennyLane circuit with an identity circuit and verify the number of gates.
    """
    n_qubits = get_number_of_qubits(simple_pennylane_circuit)
    print("n_qubits", n_qubits)
    print("simple_pennylane_circuit: ")
    print(qml.draw(simple_pennylane_circuit)())

    def all_identity(n_qubits):
        for i in range(n_qubits):
            qml.Identity(wires=i)

    def simple_prefix_circuit():
        all_identity(n_qubits)

    def joined_circuits(front_circuit, back_circuit):
        front_circuit()
        back_circuit()

    dev = qml.device("default.qubit", wires=128)
    joined_circuits_qnode = qml.QNode(joined_circuits, dev)
    print("Combined circuit:")
    print(
        qml.draw(joined_circuits)
        (simple_prefix_circuit, simple_pennylane_circuit))
    n_gates = qml.specs(joined_circuits_qnode)(
        simple_prefix_circuit, simple_pennylane_circuit)["resources"].num_gates

    assert n_gates == 6, "The joined circuit should have 6 gates."


def test_optimize_with_pennylane_simple_circuit(
        tmp_path, inefficient_pennylane_circuit):
    """
    Test that optimize_with_pennylane can optimize a simple PennyLane circuit and export it as QASM.
    """
    optimize_with_pennylane(
        inefficient_pennylane_circuit,
        var_name="simple_test",
        output_dir=tmp_path)
    all_files = os.listdir(tmp_path)
    for file in all_files:
        print(file)
        filepath = os.path.join(tmp_path, file)
        content = open(filepath, 'r').read().strip()
        assert content.startswith("OPENQASM 2.0;")


def test_optimize_with_bqskit_simple_circuit(tmp_path, simple_bqskit_circuit):
    """
    Test that optimize_with_bqskit can optimize a simple BQSKit circuit and export it as QASM.
    """
    var_name = "simple_test"
    print("simple_bqskit_circuit: ")
    print(simple_bqskit_circuit)
    optimize_with_bqskit(simple_bqskit_circuit, var_name, output_dir=tmp_path)
    all_files = os.listdir(tmp_path)
    for file in all_files:
        print(file)
        filepath = os.path.join(tmp_path, file)
        content = open(filepath, 'r').read().strip()
        assert content.startswith("OPENQASM 2.0;")
