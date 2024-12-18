#!/usr/bin/env python
# coding: utf-8

from bqskit.ext import qiskit_to_bqskit
from qiskit import qasm2

qasm_file = """
OPENQASM 2.0;
include "qelib1.inc";
gate cs q0,q1 { p(pi/4) q0; cx q0,q1; p(-pi/4) q1; cx q0,q1; p(pi/4) q1; }
qreg q[5];
cs q[4],q[0];
"""

qc = qasm2.loads(
    qasm_file, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
qc.draw()

# OUTPUT:
#      ┌─────┐
# q_0: ┤1    ├
#      │     │
# q_1: ┤     ├
#      │     │
# q_2: ┤  Cs ├
#      │     │
# q_3: ┤     ├
#      │     │
# q_4: ┤0    ├
#      └─────┘


# Import the Qiskit circuit using BQSKit
bqskit_circuit = qiskit_to_bqskit(qc)
print("BQSKit Circuit:")
print(bqskit_circuit)

# Export the BQSKit circuit to QASM
bqskit_qasm_path = "bqskit_circuit.qasm"
bqskit_circuit.save(bqskit_qasm_path)
print(f"BQSKit QASM file saved at: {bqskit_qasm_path}")

# OUTPUT:
# BQSKit Circuit:
# Circuit(5)[CSGate@(4, 0)]
# BQSKit QASM file saved at: bqskit_circuit.qasm

# read the qasm file with qiskit
with open(bqskit_qasm_path, 'r') as file:
    bqskit_qasm = file.read()
    qc_read = qasm2.loads(
        bqskit_qasm, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)


# OUTPUT:
# QASM2ParseError                           Traceback (most recent call last)
# Cell In[15], line 16
#      14 with open(bqskit_qasm_path, 'r') as file:
#      15     bqskit_qasm = file.read()
# ---> 16     qc_read = qasm2.loads(bqskit_qasm, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)

# File ~/python3.10/site-packages/qiskit/qasm2/__init__.py:587, in loads(string, include_path, custom_instructions, custom_classical, strict)
#     571 """Parse an OpenQASM 2 program from a string into a :class:`.QuantumCircuit`.
#     572
#     573 Args:
#    (...)
#     584     A circuit object representing the same OpenQASM 2 program.
#     585 """
#     586 custom_instructions = list(custom_instructions)
# --> 587 return _parse.from_bytecode(
#     588     _qasm2.bytecode_from_string(
#     589         string,
#     590         [_normalize_path(path) for path in include_path],
#     591         [
#     592             _qasm2.CustomInstruction(x.name, x.num_params, x.num_qubits, x.builtin)
#     593             for x in custom_instructions
#     594         ],
#     595         tuple(custom_classical),
#     596         strict,
#     597     ),
#     598     custom_instructions,
#     599 )

# File ~/python3.10/site-packages/qiskit/qasm2/parse.py:243, in from_bytecode(bytecode, custom_instructions)
#     240 # Pull this out as an explicit iterator so we can manually advance the loop in `DeclareGate`
#     241 # contexts easily.
#     242 bc = iter(bytecode)
# --> 243 for op in bc:
#     244     # We have to check `op.opcode` so many times, it's worth pulling out the extra attribute
#     245     # access.  We should check the opcodes in order of their likelihood to be in the OQ2 program
#     246     # for speed.  Gate applications are by far the most common for long programs.  This function
#     247     # is deliberately long and does not use hashmaps or function lookups for speed in
#     248     # Python-space.
#     249     opcode = op.opcode
#     250     # `OpCode` is an `enum` in Rust, but its instances don't have the same singleton property as
#     251     # Python `enum.Enum` objects.

# QASM2ParseError: "<input>:4,0: 'cs' is not defined in this scope"
