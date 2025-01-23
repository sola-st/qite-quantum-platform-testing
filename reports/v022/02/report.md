### QASM Export Failure: Incorrect MCX Gate Generation (using c4x instead of c3x)

## Versions
```
pytket version: 1.33.1
qiskit version: 1.2.4
```

## Expected behavior
The `mcx` gate in Qiskit should be exported to QASM as a multi-qubit controlled NOT gate with the correct number of controls and target. When reimported with Qiskit, it should not trigger an error.

## Actual behavior
When generating a circuit with a multi-qubit controlled NOT gate `mcx` (with three controls and one target) and exporting it to QASM via Pytket, it wrongly generates a `c4x` gate (which is suitable for four controls and one target). As a result, the QASM has a `c4x` gate with an invalid number of arguments, which triggers an error when reimported.

## Additional information
This issue reproduces 100% of the time. Curiously, it crashes during reimport with both Qiskit, Pennylane, and BQskit, but it works properly with Pytket. This probably points to a bug in the implementation of the `c4x` gate both when exporting and reimporting, possibly due to a misunderstanding or incorrect implementation of the specification.

## Source code
```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

qr = QuantumRegister(4)
qc = QuantumCircuit(qr)
qc.mcx([qr[0], qr[1], qr[2]], qr[3])
qc.draw()
# q2_0: ──■──
#         │
# q2_1: ──■──
#         │
# q2_2: ──■──
#       ┌─┴─┐
# q2_3: ┤ X ├
#       └───┘

from pytket.extensions.qiskit import qiskit_to_tk
from pytket.qasm import circuit_to_qasm_str

# Convert Qiskit circuit to Pytket circuit
tkqc = qiskit_to_tk(qc)

# Export optimized circuit as QASM
exported_qasm = circuit_to_qasm_str(tkqc, header='qelib1', maxwidth=200)
print(exported_qasm)
# OPENQASM 2.0;
# include "qelib1.inc";
#
# qreg q2[4];
# c4x q2[0],q2[1],q2[2],q2[3];  <-- Incorrect c4x gate generation
```

See the specification here: https://github.com/Qiskit/qiskit/blob/e9ccd3f374fd5424214361d47febacfa5919e1e3/qiskit/qasm/libs/qelib1.inc#L259

## Tracebacks
It crashes (e.g. with Qiskit) when reimporting the QASM:
```python
from qiskit.qasm2 import loads
from qiskit import qasm2

qc_imported_qiskit = loads(
    exported_qasm, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
# QASM2ParseError: "<input>:5,0: 'c4x' takes 5 quantum arguments, but got 4"
```

It works correctly (run in a notebook cell to see the rendered circuit)
```python
from pytket.qasm import circuit_from_qasm_str
from pytket.circuit.display import render_circuit_jupyter

tket_qc = circuit_from_qasm_str(exported_qasm)
render_circuit_jupyter(tket_qc)
#
# q2_0: ──■──
#         │
# q2_1: ──■──
#         │
# q2_2: ──■──
#       ┌─┴─┐
# q2_3: ┤ X ├
#       └───┘
```


## DRAFT

When generating this circuit with a multi qubit controlled not gate `mcx` (with three controls and one target) and exporting it to qasm via pytket, it wrongly generates a `c4x` gate (which is suitable for four controls and one target). As a result the qasm has a c4x gate with an invalid number of arguments which triggers an error when reimported.

```python

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

qr = QuantumRegister(4)
qc = QuantumCircuit(qr)
qc.mcx([qr[0], qr[1], qr[2]], qr[3])
qc.draw()

# q2_0: ──■──
#         │
# q2_1: ──■──
#         │
# q2_2: ──■──
#       ┌─┴─┐
# q2_3: ┤ X ├
#       └───┘

from pytket.extensions.qiskit import qiskit_to_tk
from pytket.qasm import circuit_to_qasm_str

# Convert Qiskit circuit to Pytket circuit
tkqc = qiskit_to_tk(qc)

# Export optimized circuit as QASM
exported_qasm = circuit_to_qasm_str(tkqc, header='qelib1', maxwidth=200)
print(exported_qasm)

# OPENQASM 2.0;
# include "qelib1.inc";

# qreg q2[4];
# c4x q2[0],q2[1],q2[2],q2[3];
```

When reimporting it with qiskit it triggers an error:
```python
from qiskit.qasm2 import loads
from qiskit import qasm2

qc_imported_qiskit = loads(
    exported_qasm, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
# QASM2ParseError: "<input>:5,0: 'c4x' takes 5 quantum arguments, but got 4"
```

additional info
Curiously it crashes during reimport with both qiskit, pennylane and bqskit but it works properly with pytket. This probably points to a bug in the implementation of the c4x gate both when exporting and reimporting, probably the specification was misunderstood/incorrectly implemented. (see: https://github.com/Qiskit/qiskit/blob/e9ccd3f374fd5424214361d47febacfa5919e1e3/qiskit/qasm/libs/qelib1.inc#L259)


```python
from pytket.qasm import circuit_from_qasm_str
from pytket.circuit.display import render_circuit_jupyter

tket_qc = circuit_from_qasm_str(exported_qasm)
render_circuit_jupyter(tket_qc)
# q2_0: ──■──
#         │
# q2_1: ──■──
#         │
# q2_2: ──■──
#       ┌─┴─┐
# q2_3: ┤ X ├
#       └───┘
```