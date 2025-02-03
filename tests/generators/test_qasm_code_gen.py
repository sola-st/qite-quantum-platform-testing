import pytest
from generators.qasm_code_gen import QASMCodeGenerator, H, CX, RX, U3

from qiskit import QuantumCircuit
from qiskit.qasm2 import loads


@pytest.fixture
def qasm_generator():
    return QASMCodeGenerator(num_qubits=3, seed=42)


def test_generate_header(qasm_generator):
    """
    Test that the QASM header is generated correctly.
    """
    qasm_generator.generate_header()
    qasm_code = qasm_generator.get_qasm_code()
    assert "OPENQASM 2.0;" in qasm_code
    assert 'include "qelib1.inc";' in qasm_code


def test_generate_registers(qasm_generator):
    """
    Test that the QASM registers are generated correctly.
    """
    qasm_generator.generate_registers()
    qasm_code = qasm_generator.get_qasm_code()
    assert "qreg q[3];" in qasm_code
    assert "creg c[3];" in qasm_code


def test_add_gate(qasm_generator):
    """
    Test that a gate is added correctly to the QASM code.
    """
    gate = H()
    qasm_generator.add_gate(gate)
    qasm_code = qasm_generator.get_qasm_code()
    assert "h q[" in qasm_code


def test_add_random_gate(qasm_generator):
    """
    Test that a random gate is added correctly to the QASM code.
    """
    qasm_generator.add_random_gate()
    qasm_code = qasm_generator.get_qasm_code()
    assert any(gate in qasm_code for gate in ["h q[", "cx q[", "rx(", "u3("])


def test_generate_random_qasm(qasm_generator):
    """
    Test that random QASM code is generated correctly.
    """
    qasm_generator.generate_random_qasm(num_gates=5)
    qasm_code = qasm_generator.get_qasm_code()
    assert "OPENQASM 2.0;" in qasm_code
    assert 'include "qelib1.inc";' in qasm_code
    assert "qreg q[3];" in qasm_code
    assert "creg c[3];" in qasm_code
    assert "measure q -> c;" in qasm_code
    # 2 header lines, 2 register lines, 5 gate lines, 1 measure line
    assert len(qasm_code.splitlines()) == 10


def test_import_generated_code(qasm_generator):
    """
    Test that the generated QASM code can be imported in Qiskit.
    """
    qasm_generator.generate_random_qasm(num_gates=7, final_measure=False)
    qasm_code = qasm_generator.get_qasm_code()
    print(qasm_code)
    qc = QuantumCircuit.from_qasm_str(qasm_code)

    # check number of qubits and number or gates
    assert qc.num_qubits == 3
    assert len(qc) == 7
