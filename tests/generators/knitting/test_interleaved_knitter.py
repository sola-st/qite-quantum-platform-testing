import pytest
from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
)
from generators.knitting.interleaved_knitter import InterleavedKnitter
import os
import pickle
from itertools import combinations


def test_get_register_mapping():
    """
    Test that get_register_mapping correctly creates a mapping between registers of two circuits.
    """
    # Create two quantum circuits with different registers
    qc1 = QuantumCircuit(QuantumRegister(2, 'q0'), ClassicalRegister(2, 'c0'))
    qc2 = QuantumCircuit(QuantumRegister(3, 'q1'), ClassicalRegister(3, 'c1'))

    qc1.cz(0, 1)
    qc1.cx(1, 0)
    qc1.measure(0, 0)

    qc2.cx(0, 1)
    qc2.cy(1, 2)
    qc2.measure_all(inplace=True, add_bits=False)
    print("QC1: ")
    print(qc1)
    print("QC2: ")
    print(qc2)

    # Create an instance of InterleavedKnitter
    knitter = InterleavedKnitter(qc1, qc2)

    reg1 = knitter._rename_registers(
        prefix='circ1',
        registers=qc1.qregs + qc1.cregs)
    reg2 = knitter._rename_registers(
        prefix='circ2',
        registers=qc2.qregs + qc2.cregs)

    # Get the register mapping
    mapping = knitter._get_register_mapping(
        registers_circ1=reg1,
        registers_circ2=reg2,
    )

    print(mapping)
    # Check that the mapping is correct
    assert mapping['circ2_q1'].name == 'circ2_q1'
    assert mapping['circ2_c1'].name == 'circ2_c1'
    assert mapping['circ1_q0'].name == 'circ2_q1'
    assert mapping['circ1_c0'].name == 'circ2_c1'

    combined_qc = knitter.combine_circuits()
    print("Combined QC: ")
    print(combined_qc)

    # check that the combined circuit as many operations
    # as the sum of the two circuits
    assert len(combined_qc) == len(qc1) + len(qc2)
    # check that the first operation is the first op of qc1
    assert combined_qc.data[0].name == qc1.data[0].name
    # check that the second operation is the first op of qc2
    assert combined_qc.data[1].name == qc2.data[0].name
    # check that the last operation is the last op of qc2
    assert combined_qc.data[-1].name == qc2.data[-1].name


def test_interleaved_combine_circuits():
    """
    Test that interleaved_combine_circuits correctly combines two quantum circuits in an interleaved manner.
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
        knitter = InterleavedKnitter(circuit1, circuit2)
        combined_qc = knitter.combine_circuits()
        print(f"Combined circuit:\n{combined_qc}")

        # Check that the combined circuit contains the instructions from both input circuits
        instructions = [instr.operation.name for instr in combined_qc.data]
        circuit1_instructions = [
            instr.operation.name for instr in circuit1.data]
        circuit2_instructions = [
            instr.operation.name for instr in circuit2.data]

        # Check the instructions are the same (REGARDLESS OF ORDER)
        assert all([i in set(instructions) for i in circuit1_instructions])
        assert all([i in set(instructions) for i in circuit2_instructions])
        # The sum is the same
        assert len(
            circuit1_instructions) + len(circuit2_instructions) == len(instructions)
