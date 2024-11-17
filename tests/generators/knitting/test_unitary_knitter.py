from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Operator
from generators.knitting.unitary_knitter import UnitaryKnitter
import os
import pickle
from itertools import combinations


def test_unitary_knitter_combine_circuits():
    """
    Test that combine_circuits correctly combines two quantum circuits.
    """
    # Create two simple quantum circuits
    qc1 = QuantumCircuit(2, 3)
    qc1.h(0)

    qreg = QuantumRegister(1, 'q')
    qreg2 = QuantumRegister(5, 'q2')
    creg = ClassicalRegister(1, 'c')
    qc2 = QuantumCircuit(qreg, qreg2, creg)
    qc2.x(0)
    qc2.cx(qreg[0], qreg2[0])
    qc2.measure(qreg, creg)
    print("QC1: ")
    print(qc1)
    print("QC2: ")
    print(qc2)

    # Create an instance of UnitaryKnitter
    knitter_1_in_2 = UnitaryKnitter(qc1, qc2)
    knitter_2_in_1 = UnitaryKnitter(qc2, qc1)

    # Combine the circuits
    combined_circuit = knitter_1_in_2.combine_circuits()
    print("Combined QC (QC1 injected in QC2): ")
    print(combined_circuit)

    # Check that the combined circuit contains the instructions from both input circuits
    instructions = [instr.operation.name for instr in combined_circuit.data]
    assert 'unitary' in instructions
    assert 'x' in instructions

    # Combine the circuits
    combined_circuit = knitter_2_in_1.combine_circuits()
    print("Combined QC (QC2 injected in QC1): ")
    print(combined_circuit)

    # Check that the combined circuit contains the instructions from both input circuits
    instructions = [instr.operation.name for instr in combined_circuit.data]
    assert 'unitary' in instructions
    assert 'h' in instructions


def test_unitary_knitter_combine_circuits_with_artifacts():
    """
    Test that combine_circuits correctly combines two quantum circuits from pickle files.
    """
    # Get all pickle files in the directory
    pickle_files = [f
                    for f in os.listdir(
                        'tests/artifacts/pickled_quantum_circuits')
                    if f.endswith('.pkl')]

    # Generate all combinations of two circuits
    circuit_combinations = combinations(pickle_files, 2)
    # deterministic order for testing
    circuit_combinations = sorted(list(circuit_combinations))

    for circuit1_file, circuit2_file in circuit_combinations:
        with open(f'tests/artifacts/pickled_quantum_circuits/{circuit1_file}', 'rb') as f:
            circuit1 = pickle.load(f)
        with open(f'tests/artifacts/pickled_quantum_circuits/{circuit2_file}', 'rb') as f:
            circuit2 = pickle.load(f)

        print(f"Combining {circuit1_file} and {circuit2_file}")
        print(f"Circuit 1:\n{circuit1}")
        print(f"Circuit 2:\n{circuit2}")

        # Combine the circuits
        knitter_1_in_2 = UnitaryKnitter(circuit1, circuit2)
        combined_circuit = knitter_1_in_2.combine_circuits()
        print(
            f"Combined circuit (Circuit1 injected in Circuit2):\n{combined_circuit}")

        # Check that the combined circuit contains the 'unitary' instruction
        instructions = [instr.operation.name for instr in
                        combined_circuit.data]
        assert 'unitary' in instructions
        # Check that the combined circuit has the correct number of instructions
        assert len(combined_circuit.data) == 1 + len(circuit2.data)

        # Combine the circuits in the other order
        knitter_2_in_1 = UnitaryKnitter(circuit2, circuit1)
        combined_circuit = knitter_2_in_1.combine_circuits()
        print(
            f"Combined circuit (Circuit2 injected in Circuit1):\n{combined_circuit}")

        # Check that the combined circuit contains the 'unitary' instruction
        instructions = [instr.operation.name for instr in
                        combined_circuit.data]
        assert 'unitary' in instructions
        # Check that the combined circuit has the correct number of instructions
        assert len(combined_circuit.data) == len(
            circuit1.data) + 1
