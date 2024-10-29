**Environment**

* pytket version: 1.33.1
* qiskit version: 1.2.4
* bqskit version: 1.2.0

**Expected behavior**
When creating a circuit with the `ryy` gate in Qiskit and exporting it to QASM with BQSKit, the generated QASM file should include a definition of the `ryy` gate.

**Actual behavior**
The generated QASM file does not include a definition of the `ryy` gate. When trying to read the generated QASM file with Qiskit or Pytket, an error is raised because the `ryy` gate is not defined.

**Additional information**
The `ryy` gate is not a standard gate and is not present in the [qelib1.inc](https://github.com/Qiskit/qiskit/blob/main/qiskit/qasm/libs/qelib1.inc) file. Thus, I would expect that the `ryy` gate is defined in the QASM file.


**Source code**

```python
from bqskit.ext import qiskit_to_bqskit
from qiskit.qasm2 import dumps, loads
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

qc = QuantumCircuit(2)
qc.ryy(0.1, 0, 1)

# Export with Qiskit
qasm = dumps(qc)
print("-"*4)
print("Exported by Qiskit")
print(qasm)

# Export with BQSKit
bqskit_circ = qiskit_to_bqskit(qc)
bqskit_circ.save("bqskit.qasm")
with open("bqskit.qasm", "r") as f:
    qasm_str_from_bqskit = f.read()
print("-"*4)
print("Exported by BQSKit")
print(qasm_str_from_bqskit)
# ----
# Exported by Qiskit
# OPENQASM 2.0;
# include "qelib1.inc";
# gate ryy(param0) q0,q1 { rx(pi/2) q0; rx(pi/2) q1; cx q0,q1; rz(param0) q1; cx q0,q1; rx(-pi/2) q0; rx(-pi/2) q1; }
# qreg q[2];
# ryy(0.1) q[0],q[1];
# ----
# Exported by BQSKit
# OPENQASM 2.0;
# include "qelib1.inc";
# qreg q[2];
# ryy(0.1) q[0], q[1];
```

**Tracebacks**

When reading the generated QASM file with Qiskit:
```python
from qiskit import qasm2
qiskit_read_back = loads(qasm_str_from_bqskit)
# QASM2ParseError: "<input>:4,0: 'ryy' is not defined in this scope"
```

When reading the generated QASM file with Pytket:
```python
from pytket.qasm import circuit_from_qasm_str
tket_circuit = circuit_from_qasm_str(qasm_str_from_bqskit)
# QASMParseError: Cannot parse gate of type: ryy Line:4.
```
