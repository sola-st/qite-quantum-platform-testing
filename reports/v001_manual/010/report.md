`n` Duplicated Classical Register Definition (for register of size `n`) when saving QASM file

**Environment**

* pytket version: 1.33.1
* qiskit version: 1.2.4
* bqskit version: 1.2.0

**Expected behavior**
When creating a simple empty circuit with a single final measurement, the exported QASM file should have only one definition for the classical register.

**Actual behavior**
The exported QASM file has two definitions for the classical register, which leads to an invalid QASM file that cannot be imported by either BQSKit or Qiskit.

**Additional information**
The reproducibility of this issue is full (100%). The error is raised every time the circuit is exported and imported.

**Source code**
Here is the minimal example to generate the buggy QASM file:

```python
from bqskit.ext import qiskit_to_bqskit
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

# Section: Circuit
qr = QuantumRegister(2, name='qr')
cr = ClassicalRegister(2, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')

qc.measure(qr, cr)

bqc = qiskit_to_bqskit(qc)
print(bqc)
# Circuit(2)[measurement@(0,), measurement@(1,)]
bqc.save('file.qasm')
# OPENQASM 2.0;
# include "qelib1.inc";
# qreg q[2];
# creg cr[2];
# creg cr[2];
# measure q[0] -> cr[0];
# measure q[1] -> cr[1];
```

**Tracebacks**

When trying to import the QASM file with Qiskit:
```python
from qiskit.qasm2 import load
qc = load('file.qasm')
# QASM2ParseError: "file.qasm:5,5: 'cr' is already defined"
```

When trying to import the QASM file with BQSKit:
```python
from bqskit import Circuit
bqc = Circuit.from_file('file.qasm')
# LangException: Classical register redeclared: cr.
```

**Potential Solution/Insight:**

The issue may be due to the exporter generating duplicate instructions for classical registers. This could be caused by a bug in the QASM generation or instruction creation process. Investigating the generation of QASM for classical registers may help identify the root cause of the issue, which may be related to the number of times the register is exported.
Note that when the size of the register is n the number of times the register is exported is n (tested with size up to n=32).
This seems to happen because of the presence of the `qc.measure(qr, cr)` instruction, so the issue may be related to the handling of this instruction in the QASM generation process.