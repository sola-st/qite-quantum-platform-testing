

# TITLE
`FullPeepholeOptimise` Pass Failures with `u0` and `c4x` Gates

## System

```python
import qiskit
import pytket
print(f"Qiskit version: {qiskit.__version__}")
print(f"Pytket version: {pytket.__version__}")
```

Output:

```
Qiskit version: 1.2.0
Pytket version: 1.31.1
```
### Expected behavior
The `FullPeepholeOptimise` pass should successfully optimize the circuit without throwing any errors, regardless of the presence of custom gates like `u0` and `c4x`.

### Actual behavior
The `FullPeepholeOptimise` pass fails with a `RuntimeError` when the circuit contains both `u0` and `c4x` gates, with the error message: `Operation is not a gate: CustomGate`.

### Additional information
The issue is reproducible 100% of the time when both `u0` and `c4x` gates are present in the circuit. If only one of these gates is present, the pass applies successfully.

### Source code
```python
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit
from pytket.qasm import circuit_from_qasm_str
qasm_str = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
u0(4) q[0];
c4x q[0],q[1],q[2],q[3],q[4];
"""
tket_circ = circuit_from_qasm_str(qasm_str)

qc = tk_to_qiskit(tket_circ)
print(qc)
# OUTPUT
#      ┌──────────┐
# q_0: ┤ u0(4/pi) ├──■──
#      └──────────┘  │
# q_1: ──────────────■──
#                    │
# q_2: ──────────────■──
#                    │
# q_3: ──────────────■──
#                  ┌─┴─┐
# q_4: ────────────┤ X ├
#                  └───┘

from pytket.passes import FullPeepholeOptimise
from copy import deepcopy

optimization_pass = FullPeepholeOptimise()

print("Applying FullPeepholeOptimise")
i_qc = deepcopy(tket_circ)
optimization_pass.apply(i_qc)
# OUTPUT
# Applying FullPeepholeOptimise
```

### Tracebacks
```python
RuntimeError                              Traceback (most recent call last)
Cell In[43], line 34
     32 print("Applying FullPeepholeOptimise")
     33 i_qc = deepcopy(tket_circ)
---> 34 optimization_pass.apply(i_qc)
     35 # OUTPUT
     36 # Applying FullPeepholeOptimise

RuntimeError: Operation is not a gate: CustomGate
```

Thanks in advance. If you need any additional information I will be happy to provide it.


# Draft

Running the fullpeephole optimization pass on a circuit with
c4x and u0 gates at the same time fails with the error message:
`Operation is not a gate: CustomGate`.

This does not happen if there is only one of the two gate, this happens only when both are present in the circuit.


This is the code:
```python
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit
from pytket.qasm import circuit_from_qasm_str
qasm_str = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
u0(4) q[0];
c4x q[0],q[1],q[2],q[3],q[4];
"""
tket_circ = circuit_from_qasm_str(qasm_str)

qc = tk_to_qiskit(tket_circ)
print(qc)

# OUTPUT
#      ┌──────────┐
# q_0: ┤ u0(4/pi) ├──■──
#      └──────────┘  │
# q_1: ──────────────■──
#                    │
# q_2: ──────────────■──
#                    │
# q_3: ──────────────■──
#                  ┌─┴─┐
# q_4: ────────────┤ X ├
#                  └───┘

from pytket.passes import FullPeepholeOptimise

optimization_pass = FullPeepholeOptimise()

print("Applying FullPeepholeOptimise")
i_qc = deepcopy(tket_circ)
optimization_pass.apply(i_qc)

# OUTPUT
# Applying FullPeepholeOptimise
# ---------------------------------------------------------------------------
# RuntimeError                              Traceback (most recent call last)
# Cell In[42], line 8
#       6 print("Applying FullPeepholeOptimise")
#       7 i_qc = deepcopy(tket_circ)
# ----> 8 optimization_pass.apply(i_qc)

# RuntimeError: Operation is not a gate: CustomGate

```