
**Title**: 🐛 Error parsing `ms` gate in OpenQASM with mqt-core.

### **Environment Information**
```plaintext
- OS: Ubuntu 20.04
- C++ Compiler: g++ (Ubuntu 9.4.0-1ubuntu1~20.04.2) 9.4.0
- mqt.core version: 2.7.0
- mqt.qcec version: 2.7.1
- Qiskit version: 1.2.0
```

### **Description**
The `ms` gate is not correctly parsed by mqt-core, resulting in a `RuntimeError` when trying to verify or parse the circuit.

### **Expected Behavior**
The `ms` gate should be correctly parsed by mqt-core, as it is valid and can be created by Qiskit. A similar circuit parses without issue in Qiskit.

---

### **How to Reproduce**
#### **Steps to Reproduce**
1. Create a circuit with Qiskit that includes the `ms` gate.
2. Export the circuit to OpenQASM using Qiskit’s `qasm2.dumps()` function.
3. Attempt to verify the circuit using mqt-core with:
    ```python
    from mqt import qcec
    result = qcec.verify("path_to_circuit.qasm", "path_to_another_circuit.qasm")
    print(result)
    ```

#### **Example Code Snippet**
Create a circuit with Qiskit that includes the `ms` gate.
```python
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.ms(0.844396, [qr[0], qr[1], qr[2]])
qc.measure(qr, cr)

from qiskit import qasm2
qasm_string_a = qasm2.dumps(qc)
print(qasm_string_a)
```

Export the circuit to OpenQASM.
```plaintext
OPENQASM 2.0;
include "qelib1.inc";
gate ms(param0) q0,q1,q2 { rxx(0.844396) q0,q1; rxx(0.844396) q0,q2; rxx(0.844396) q1,q2; }
qreg qr[3];
creg cr[3];
ms(0.844396) qr[0],qr[1],qr[2];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
```

Attempt to verify the circuit using mqt-core.
```python
from mqt import qcec
qasm_string_a = """
OPENQASM 2.0;
include "qelib1.inc";
gate ms(param0) q0,q1,q2 { rxx(0.844396) q0,q1; rxx(0.844396) q0,q2; rxx(0.844396) q1,q2; }
qreg qr[3];
creg cr[3];
ms(0.844396) qr[0],qr[1],qr[2];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
"""

path_a = "a.qasm"
with open(path_a, "w") as f:
    f.write(qasm_string_a)

result = qcec.verify(path_a, "b.qasm")
print(result)
```

#### **Error Produced**
```plaintext
RuntimeError: Could not import first circuit: <input>:4:6: Expected 'Identifier', got 'ms'.
```

Alternatively, using the `mqt.core` library directly, without `mqt.qcec`, also results in the same error.
```python
from mqt.core import QuantumComputation
qasm_string_a = """
OPENQASM 2.0;
OPENQASM 2.0;
include "qelib1.inc";
gate ms(param0) q0,q1,q2 { rxx(0.844396) q0,q1; rxx(0.844396) q0,q2; rxx(0.844396) q1,q2; }
qreg qr[3];
creg cr[3];
ms(0.844396) qr[0],qr[1],qr[2];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
"""
QuantumComputation.from_qasm(qasm_string_a)
# RuntimeError: <input>:4:6: Expected 'Identifier', got 'ms'.
```

However, the same circuit can be parsed without issue using Qiskit's `qasm` module.
```python
from mqt.core import QuantumComputation
qasm_string_a = """
OPENQASM 2.0;
include "qelib1.inc";
gate ms_test(param0) q0,q1,q2 { rxx(0.844396) q0,q1; rxx(0.844396) q0,q2; rxx(0.844396) q1,q2; }
qreg qr[3];
creg cr[3];
ms_test(0.844396) qr[0],qr[1],qr[2];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
"""
QuantumComputation.from_qasm(qasm_string_a)
```
Output:
```plaintext

i:   0   1   2
1:------------
 : rxx rxx   |  p: (0.844396)
 : rxx   | rxx  p: (0.844396)
 :   | rxx rxx  p: (0.844396)
 -------------
2:   0   |   |
3:   |   1   |
4:   |   |   2
o:   0   1   2
```

#### **Possible Problem**
The issue seems to be related to the parsing of the `ms` gate. The error message indicates the problem occurs when `ms` is used, suggesting that the parser might be incorrectly handling this gate's name. This could be due to the parser's check for expected tokens in `mqt-core/include/mqt-core/ir/parsers/qasm3_parser/Scanner.hpp`.
```cpp
void expect(const char expected) {
    if (ch != expected) {
        error("Expected '" + std::to_string(expected) + "', got '" + ch + "'");
    } else {
        nextCh();
    }
}
```