## `FullPeepholeOptimise` Pass Failure: Unitary1qBox Operation not Recognized

## Versions
```
pytket version: 1.33.1
qiskit version: 1.2.4
```

## Expected behavior
I expect the `FullPeepholeOptimise` pass to optimize the given circuit and apply the necessary transformations without raising any runtime errors.

## Actual behavior
The `FullPeepholeOptimise` pass raises a `RuntimeError` when applied to the given circuit, indicating that an operation is not a gate: `Unitary1qBox`. In contrast, other passes like `PeepholeOptimise2Q` work correctly and optimize the circuit without any crashes.

## Additional information
The issue can be reproduced consistently with the provided code snippet. It seems that the `FullPeepholeOptimise` pass is not able to handle the `Unitary1qBox` operation correctly, leading to the runtime error.

## Source code
```python
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

from pytket.extensions.qiskit import qiskit_to_tk
from pytket.passes import FullPeepholeOptimise, PeepholeOptimise2Q
from pytket.qasm import circuit_to_qasm_str

qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')

qc.mcrz(1.23, [qr[0], qr[1]], qr[2])
print(qc.draw())

# Convert Qiskit circuit to Pytket circuit
tkqc = qiskit_to_tk(qc)

# Apply Full Peephole Optimization
FullPeepholeOptimise().apply(tkqc)
# CRASH: RuntimeError: Operation is not a gate: Unitary1qBox

# Applying PeepholeOptimise2Q works correctly
# PeepholeOptimise2Q().apply(tkqc)
# Export optimized circuit as QASM
# opt_circuit_qasm = circuit_to_qasm_str(tkqc, header='qelib1', maxwidth=200)
# print(opt_circuit_qasm)
```
### Tracebacks
```python
---------------------------------------------------------------------------
RuntimeError                              Traceback (most recent call last)
Cell In[32], line 19
     16 tkqc = qiskit_to_tk(qc)
     18 # Apply Full Peephole Optimization
---> 19 FullPeepholeOptimise().apply(tkqc)
     20 # CRASH: RuntimeError: Operation is not a gate: Unitary1qBox
     21
     22 # Apply Peephole Optimization 2Q
   (...)
     25
     26 # Export optimized circuit as QASM
     27 opt_circuit_qasm = circuit_to_qasm_str(tkqc, header='qelib1', maxwidth=200)

RuntimeError: Operation is not a gate: Unitary1qBox
```
### Additional Information
Full code snippets and outputs:
- When using `PeepholeOptimise2Q`:
```qasm
OPENQASM 2.0;
include "qelib1.inc";

qreg qr[3];
creg cr[3];
cx qr[0],qr[2];
u3(0.0*pi,3.4021197099984843*pi,0.5*pi) qr[2];
cx qr[1],qr[2];
u3(0.0*pi,-0.4021197099984844*pi,0.5*pi) qr[2];
cx qr[0],qr[2];
u3(0.0*pi,3.4021197099984843*pi,0.5*pi) qr[2];
cx qr[1],qr[2];
u3(0.0*pi,-0.4021197099984844*pi,0.5*pi) qr[2];
```
- Original Circuit:
```txt
qr_0: ──■───────────────────────────────■─────────────────────────────
        │                               │
qr_1: ──┼───────────────■───────────────┼───────────────■─────────────
      ┌─┴─┐┌─────────┐┌─┴─┐┌─────────┐┌─┴─┐┌─────────┐┌─┴─┐┌─────────┐
qr_2: ┤ X ├┤ Unitary ├┤ X ├┤ Unitary ├┤ X ├┤ Unitary ├┤ X ├┤ Unitary ├
      └───┘└─────────┘└───┘└─────────┘└───┘└─────────┘└───┘└─────────┘
cr: 3/════════════════════════════════════════════════════════════════
```

Thanks in advance. If you need any additional information I will be happy to provide it.





# DRAFT


When running the optimization pass `FullPeepholeOptimise` it raise the runtime error instead of converting the circuit to an optimized version.
Conversely any other pass runs correctly (e.g. `PeepholeOptimise2Q`) without crashes converting the circuit to an optimized version.

```python
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

from pytket.extensions.qiskit import qiskit_to_tk
from pytket.passes import FullPeepholeOptimise, PeepholeOptimise2Q
from pytket.qasm import circuit_to_qasm_str

qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')

qc.mcrz(1.23, [qr[0], qr[1]], qr[2])
print(qc.draw())

# Convert Qiskit circuit to Pytket circuit
tkqc = qiskit_to_tk(qc)

# Apply Full Peephole Optimization
FullPeepholeOptimise().apply(tkqc)
## CRASH: RuntimeError: Operation is not a gate: Unitary1qBox

```

Circuit:
```txt
qr_0: ──■───────────────────────────────■─────────────────────────────
        │                               │
qr_1: ──┼───────────────■───────────────┼───────────────■─────────────
      ┌─┴─┐┌─────────┐┌─┴─┐┌─────────┐┌─┴─┐┌─────────┐┌─┴─┐┌─────────┐
qr_2: ┤ X ├┤ Unitary ├┤ X ├┤ Unitary ├┤ X ├┤ Unitary ├┤ X ├┤ Unitary ├
      └───┘└─────────┘└───┘└─────────┘└───┘└─────────┘└───┘└─────────┘
cr: 3/════════════════════════════════════════════════════════════════
```

Replacing with `PeepholeOptimise2Q

```python
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

from pytket.extensions.qiskit import qiskit_to_tk
from pytket.passes import FullPeepholeOptimise, PeepholeOptimise2Q
from pytket.qasm import circuit_to_qasm_str

qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')

qc.mcrz(1.23, [qr[0], qr[1]], qr[2])
print(qc.draw())

# Convert Qiskit circuit to Pytket circuit
tkqc = qiskit_to_tk(qc)

# Apply Peephole Optimization 2Q
PeepholeOptimise2Q().apply(tkqc)
## Working: No crash

# Export optimized circuit as QASM
opt_circuit_qasm = circuit_to_qasm_str(tkqc, header='qelib1', maxwidth=200)
print(opt_circuit_qasm)
```

Output QASM:
```qasm
OPENQASM 2.0;
include "qelib1.inc";

qreg qr[3];
creg cr[3];
cx qr[0],qr[2];
u3(0.0*pi,3.4021197099984843*pi,0.5*pi) qr[2];
cx qr[1],qr[2];
u3(0.0*pi,-0.4021197099984844*pi,0.5*pi) qr[2];
cx qr[0],qr[2];
u3(0.0*pi,3.4021197099984843*pi,0.5*pi) qr[2];
cx qr[1],qr[2];
u3(0.0*pi,-0.4021197099984844*pi,0.5*pi) qr[2];
```
