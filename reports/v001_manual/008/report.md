**Expected behavior**
We expect to be able to convert a Qiskit circuit to a BQSKit circuit and then save it as a QASM file without any issues.

**Actual behavior**
The conversion and saving process fails with an `AttributeError` when trying to save the QASM file.

**Additional information**
This issue seems to be related to the `sxdg` gate (Sqrt(X) dagger) in the Qiskit circuit. The error occurs because BQSKit's `DaggerGate` object does not have a `_qasm_name` attribute, which is required for QASM encoding.

**Source code**
```python
# Qiskit circuit creation
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
qr = QuantumRegister(1, name='qr')
cr = ClassicalRegister(1, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.sxdg(qr[0])
qc.measure(qr, cr)

# BQSKit conversion and saving
from bqskit.ext import qiskit_to_bqskit
circuit = qiskit_to_bqskit(qc)
circuit.save('check.qasm')
# Output: (AttributeError is raised)
# AttributeError: 'DaggerGate' object has no attribute '_qasm_name'
```

**Tracebacks**
```
AttributeError                            Traceback (most recent call last)
Cell In[9], line 3
      1 from bqskit.ext import qiskit_to_bqskit
      2 circuit = qiskit_to_bqskit(qc)
----> 3 circuit.save('check.qasm')

File ../site-packages/bqskit/ir/circuit.py:3246, in Circuit.save(self, filename)
   3243 language = get_language(filename.split('.')[-1])
   3245 with open(filename, 'w') as f:
-> 3246     f.write(language.encode(self))

File ../site-packages/bqskit/ir/lang/qasm2/qasm2.py:29, in OPENQASM2Language.encode(self, circuit)
     26     source += gate.get_qasm_gate_def()
     28 for op in circuit:
---> 29     source += op.get_qasm()
     31 return source

File ../site-packages/bqskit/ir/operation.py:101, in Operation.get_qasm(self)
     98 else:
     99     full_params = self.params
--> 101 return self.gate.get_qasm(full_params, self.location)

File ../site-packages/bqskit/ir/gate.py:50, in Gate.get_qasm(self, params, location)
     47 def get_qasm(self, params: RealVector, location: CircuitLocation) -> str:
     48     """Returns the qasm string for this gate."""
     49     return '{}({}) q[{}];\n'.format(
---> 50         self.qasm_name,
     51         ', '.join([str(p) for p in params]),
     52         '], q['.join([str(q) for q in location]),
     53     ).replace('()', '')

File ../site-packages/bqskit/ir/gate.py:38, in Gate.qasm_name(self)
     35 if not self.is_qubit_only():
     36     raise AttributeError('QASM only supports qubit gates.')
---> 38 return getattr(self, '_qasm_name')

AttributeError: 'DaggerGate' object has no attribute '_qasm_name'
```