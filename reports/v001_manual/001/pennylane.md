## OFFICIAL BUG REPORT

### Expected Behavior
When the script is executed, the SX operation should be applied to the qubit at index 1, as specified in the circuit definition. The QASM string generated from the circuit should reflect this and include the correct operation on the correct qubit.

### Actual Behavior
Instead, the SX operation is applied to the first free qubit (at index 0), not the one at index 1. This is evident in the QASM string generated from the circuit, where the SX operation is applied to q[0] instead of q[1].

### Additional Information
The issue is reproducible 100% of the time. Further testing with more complex circuits has confirmed that the operations are consistently applied to the first free qubit instead of the one specified in the circuit.

The issue is likely linked to the self.wires of the QuantumScript class, as they are not ordered in numeric order.


### Source Code
```python
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=3)

@qml.qnode(dev)
def circuit():
    qml.SX(wires=1)
    return [
        qml.expval(qml.PauliZ(0)),
        qml.expval(qml.PauliZ(1)),
        qml.expval(qml.PauliZ(2)),
    ]


np.random.seed(1)
print("--------------------")
print("Circuit:")
print(qml.draw(circuit, level="device")())

from pennylane.tape import QuantumTape

with QuantumTape(shots=10) as tape:
    circuit.construct([], {})
    qasm_str_pennylane = circuit.tape.to_openqasm()
print("--------------------")
print("QASM string from PennyLane:")
print(qasm_str_pennylane)
# --------------------
# Circuit:
# 0: ─────┤  <Z>
# 1: ──SX─┤  <Z>
# 2: ─────┤  <Z>
# --------------------
# QASM string from PennyLane:
# OPENQASM 2.0;
# include "qelib1.inc";
# qreg q[3];
# creg c[3];
# rz(1.5707963267948966) q[0];
# ry(1.5707963267948966) q[0];
# rz(-3.141592653589793) q[0];
# u1(1.5707963267948966) q[0];
# measure q[0] -> c[0];
# measure q[1] -> c[1];
# measure q[2] -> c[2];
```

### Traceback
No error traceback is produced, as the code executes without errors. However, the output is incorrect, and the QASM string does not represent the correct circuit.

### System Information
Name: PennyLane
Version: 0.38.0
Summary: PennyLane is a cross-platform Python library for quantum computing, quantum machine learning, and quantum chemistry. Train a quantum computer the same way as a neural network.
Home-page: https://github.com/PennyLaneAI/pennylane
Author:
Author-email:
License: Apache License 2.0
Location: /usr/local/lib/python3.10/site-packages
Requires: appdirs, autograd, autoray, cachetools, networkx, numpy, packaging, pennylane-lightning, requests, rustworkx, scipy, toml, typing-extensions
Required-by: PennyLane-qiskit, PennyLane_Lightning

Platform info:           Linux-5.4.0-193-generic-x86_64-with-glibc2.36
Python version:          3.10.15
Numpy version:           1.26.4
Scipy version:           1.14.1
Installed devices:
- lightning.qubit (PennyLane_Lightning-0.38.0)
- qiskit.aer (PennyLane-qiskit-0.38.0)
- qiskit.basicaer (PennyLane-qiskit-0.38.0)
- qiskit.basicsim (PennyLane-qiskit-0.38.0)
- qiskit.remote (PennyLane-qiskit-0.38.0)
- default.clifford (PennyLane-0.38.0)
- default.gaussian (PennyLane-0.38.0)
- default.mixed (PennyLane-0.38.0)
- default.qubit (PennyLane-0.38.0)
- default.qubit.autograd (PennyLane-0.38.0)
- default.qubit.jax (PennyLane-0.38.0)
- default.qubit.legacy (PennyLane-0.38.0)
- default.qubit.tf (PennyLane-0.38.0)
- default.qubit.torch (PennyLane-0.38.0)
- default.qutrit (PennyLane-0.38.0)
- default.qutrit.mixed (PennyLane-0.38.0)
- default.tensor (PennyLane-0.38.0)
- null.qubit (PennyLane-0.38.0)


## BUG REPORT
Running this script:
```python
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=3)

@qml.qnode(dev)
def circuit():
    qml.SX(wires=1)
    return [
        qml.expval(qml.PauliZ(0)),
        qml.expval(qml.PauliZ(1)),
        qml.expval(qml.PauliZ(2)),
    ]


np.random.seed(1)
print("--------------------")
print("Circuit:")
print(qml.draw(circuit, level="device")())

from pennylane.tape import QuantumTape

with QuantumTape(shots=10) as tape:
    circuit.construct([], {})
    qasm_str_pennylane = circuit.tape.to_openqasm()
print("--------------------")
print("QASM string from PennyLane:")
print(qasm_str_pennylane)
```
Leads to the following output:
```python
# --------------------
# Circuit:
# 0: ─────┤  <Z>
# 1: ──SX─┤  <Z>
# 2: ─────┤  <Z>
# --------------------
# QASM string from PennyLane:
# OPENQASM 2.0;
# include "qelib1.inc";
# qreg q[3];
# creg c[3];
# rz(1.5707963267948966) q[0];
# ry(1.5707963267948966) q[0];
# rz(-3.141592653589793) q[0];
# u1(1.5707963267948966) q[0];
# measure q[0] -> c[0];
# measure q[1] -> c[1];
# measure q[2] -> c[2];
```
Where the operation `SX` is added to the first free qubit instead of the one at index 1. This is present also with more complex circuits, the operations are added to the first free qubit instead of the one specified in the circuit. I did some other tests to confirm that.
There is no bug but simply a non semantically equivalent representation of the circuit.
I would have expected the `SX` operation to be added to the qubit at index 1, since if I measure the output of the circuit and convert it to a decimal number it would be wrong.
The problem is likely linked to the self.wires of the class `QuantumScript` since they are not ordered in numeric order.





# ORGINAL ERROR

Before Exporting to QASM
```
0: --------------------------------------┤  <Z>
1: ----U1(-1.57)----U2(0.00,3.14)----U1(-1.57)----┤  <Z>
2: --------------------------------------┤  <Z>
3: --------------------------------------┤  <Z>
4: --------------------------------------┤  <Z>
```

After exporting to QASM:
```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[5];
u1(-1.5707963267948966) q[0];
u2(0.0,3.141592653589793) q[0];
u1(-1.5707963267948966) q[0];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
```

Where:
- Platform: PennyLane
- Component: Exporting to QASM