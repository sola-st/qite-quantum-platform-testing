import pickle
from qiskit import QuantumCircuit
from qiskit import ClassicalRegister, QuantumRegister
import os
from itertools import combinations
import random
from generators.knitting.sequential_knitter import SequentialKnitter


def test_sequential_combine_circuits():
    """
    Test that sequential_combine_circuits correctly combines two quantum circuits sequentially.
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

        # fix seed for reproducibility
        random.seed(0)
        # Combine the circuits
        knitter = SequentialKnitter(circuit1, circuit2)
        combined_qc = knitter.combine_circuits()
        print(f"Combined circuit:\n{combined_qc}")

        # Check that the combined circuit has the correct number of qubits and classical bits
        assert combined_qc.num_qubits == max(
            circuit1.num_qubits, circuit2.num_qubits)
        assert combined_qc.num_clbits == max(
            circuit1.num_clbits, circuit2.num_clbits)

        # Check that the combined circuit contains the instructions from both input circuits
        instructions = [instr.operation.name
                        for instr in combined_qc.data]
        circuit1_instructions = [
            instr.operation.name for instr in circuit1.data]
        circuit2_instructions = [
            instr.operation.name for instr in circuit2.data]

        print("All Instructions")
        print(instructions)
        print("Circuit 1 Instructions")
        print(circuit1_instructions)
        print("Circuit 2 Instructions")
        print(circuit2_instructions)

        # check the instructions are the same (REGARDLESS OF ORDER)
        assert all([i in set(instructions) for i in circuit1_instructions])
        assert all([i in set(instructions) for i in circuit2_instructions])
        # the sum is the same
        assert len(circuit1_instructions) + len(circuit2_instructions) == len(
            instructions)
