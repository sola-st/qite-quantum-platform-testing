import pickle
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

from generators.combine_circuits import assign_random_params
from generators.combine_circuits import combine_circuits
import os
from itertools import combinations
import random


def test_assign_random_params():
    """
    Test that assign_random_params assigns random values to all unbound parameters in the circuit.
    """
    # Create a quantum circuit with unbound parameters
    theta = Parameter('θ')
    phi = Parameter('φ')
    qc = QuantumCircuit(1)
    qc.rx(theta, 0)
    qc.ry(phi, 0)

    # Assign random parameters
    qc_with_params = assign_random_params(qc)

    # Check that all parameters are now bound
    assert len(qc_with_params.parameters) == 0

    # Check that the parameters are within the expected range
    for instruction in qc_with_params.data:
        for param in instruction.operation.params:
            assert 0 <= param <= 2 * 3.14159


def test_combine_circuits():
    """
    Test that combine_circuits correctly combines two quantum circuits sequentially.
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
        combined_qc = combine_circuits(circuit1, circuit2)
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

        # check the instructions are the same (REGARDLESS OF ORDER)
        assert all([i in set(instructions) for i in circuit1_instructions])
        assert all([i in set(instructions) for i in circuit2_instructions])
        # the sum is the same
        assert len(circuit1_instructions) + len(circuit2_instructions) == len(
            instructions)
