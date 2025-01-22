Pytket ZXGraphlikeOptimisation Pass Failing to Preserve Circuit Equivalence


## Expected behavior
The circuit optimized using the ZX-calculus via the function pass `ZXGraphlikeOptimisation` should be equivalent to the original circuit.

## Actual behavior
The optimized circuit is not equivalent to the original one. The unitary matrices of the two circuits are different, indicating that they represent different quantum operations.

## Additional information
The issue reproduces consistently, every time the code is run. The QCEC tool also confirms that the two circuits are not equivalent.

## Source code
```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

from pytket.extensions.qiskit import qiskit_to_tk
from pytket.qasm import circuit_to_qasm_str
from pytket.passes import ZXGraphlikeOptimisation


tk_circ = qiskit_to_tk(qc)

optimization_pass = ZXGraphlikeOptimisation()
optimization_pass.apply(tk_circ)
opt_circ_qasm = circuit_to_qasm_str(
    tk_circ, header="qelib1", maxwidth=200)
print(opt_circ_qasm)
# Output:
# OPENQASM 2.0;
# include "qelib1.inc";
#
# qreg q[2];
# cz q[0],q[1];
# h q[0];
# h q[1];
# cz q[0],q[1];
# h q[1];
```

## Tracebacks
There are no direct error tracebacks related to the issue. However, the verification using the QCEC tool and the composition of the circuits reveal that the optimized circuit is not equivalent to the original one.
```python

qasm_a = """
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
cz q[0],q[1];
h q[0];
h q[1];
cz q[0],q[1];
h q[1];
"""

qasm_b = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
"""

from mqt import qcec
result = qcec.verify(
    qc_a, qc_b,
    transform_dynamic_circuit=True)
equivalence = str(result.equivalence)
result.equivalence
# OUTPUT
# <EquivalenceCriterion.not_equivalent: 0>

qc_mixed = Operator(qc_a).compose(Operator(qc_b).adjoint())
unitary_mixed = qc_mixed.data
# round all entries to the 3rd decimal
unitary_mixed = np.round(unitary_mixed, 3)
print("\nUnitary of qc_a * qc_b^-1:")
print(unitary_mixed)

# OUTPUT
# Unitary of qc_a * qc_b^-1:
# [[ 1.+0.j  0.+0.j  0.+0.j  0.+0.j]
#  [ 0.+0.j  1.+0.j  0.+0.j  0.+0.j]
#  [ 0.+0.j  0.+0.j  1.+0.j  0.+0.j]
#  [ 0.+0.j  0.+0.j -0.+0.j -1.+0.j]]
```


## Additional context

Here you can see how the unitary matrices of the two circuits are different:
```python
qasm_a = """
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
cz q[0],q[1];
h q[0];
h q[1];
cz q[0],q[1];
h q[1];
"""

qasm_b = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
"""

import numpy as np
from numpy.testing import assert_allclose
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

# Read the QASM strings into quantum circuits
qc_a = QuantumCircuit.from_qasm_str(qasm_a)
qc_b = QuantumCircuit.from_qasm_str(qasm_b)

# Get the unitary matrices
unitary_a = Operator(qc_a).data
unitary_b = Operator(qc_b).data

# Print the unitary matrices
print("Unitary of qc_a:")
print(unitary_a)

print("\nUnitary of qc_b:")
print(unitary_b)

# assert that they are the same
assert unitary_a.shape == unitary_b.shape
# assert_allclose(unitary_a, unitary_b, atol=1e-5)
import numpy as np
# flatten the two and the iterate element by element and print when two are different
for a, b in zip(unitary_a.flatten(), unitary_b.flatten()):
    if not np.isclose(a, b, atol=1e-5):
        print("Different elements:")
        print(a, b)
        break
# OUTPUT:
# Unitary of qc_a:
# [[ 0.70710678+0.j  0.70710678+0.j  0.        +0.j  0.        +0.j]
#  [ 0.        +0.j  0.        +0.j  0.70710678+0.j  0.70710678+0.j]
#  [ 0.        +0.j  0.        +0.j  0.70710678+0.j -0.70710678+0.j]
#  [ 0.70710678+0.j -0.70710678+0.j  0.        +0.j  0.        +0.j]]

# Unitary of qc_b:
# [[ 0.70710678+0.j  0.70710678+0.j  0.        +0.j  0.        +0.j]
#  [ 0.        +0.j  0.        +0.j  0.70710678+0.j -0.70710678+0.j]
#  [ 0.        +0.j  0.        +0.j  0.70710678+0.j  0.70710678+0.j]
#  [ 0.70710678+0.j -0.70710678+0.j  0.        +0.j  0.        +0.j]]
# Different elements:
# (0.7071067811865474+0j) (-0.7071067811865475+0j)
```

Let me know if you need more information, thanks in advance!
