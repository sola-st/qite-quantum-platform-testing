Running this import:

```python
qasm_string_a = """
OPENQASM 2.0;
include "qelib1.inc";
gate ms(param0) q0,q1,q2 { rxx(0.844396) q0,q1; rxx(0.844396) q0,q2; rxx(0.844396) q1,q2; }
qreg qr[3];
creg cr[3];
ms(0.844396) qr[3],qr[16],qr[22];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
"""
# write to file
path_a = "a.qasm"
with open(path_a, "w") as f:
    f.write(qasm_string_a)

qasm_string_b = """
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[3];
creg cr[3];
h qr[0];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
"""
# write to file
path_b = "b.qasm"
with open(path_b, "w") as f:
    f.write(qasm_string_b)

from mqt import qcec
result = qcec.verify(path_a, path_b)
print(result)
```

It fails with error:
```python
RuntimeError: Could not import first circuit: <input>:3:6:
Expected 'Identifier', got 'ms'.
```

The program was created with qiskit:
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
Output:
```
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



## Possible Problem

In file: `mqt-qcec/src/EquivalenceCheckingManager.cpp`
```cpp
EquivalenceCheckingManager::EquivalenceCheckingManager(
    // Circuits not passed by value and moved because this would cause slicing.
    // NOLINTNEXTLINE(modernize-pass-by-value)
    const qc::QuantumComputation& circ1, const qc::QuantumComputation& circ2,
    Configuration config)
    : qc1(circ1), qc2(circ2), configuration(std::move(config)) {
```

The `qc1` and `qc2` are read with `#include "ir/QuantumComputation.hpp`
defined in the `mqt-core` project. The `QuantumComputation` class is defined as:

In file: `mqt-core/src/ir/QuantumComputation.cpp`
```cpp
void QuantumComputation::import(const std::string& filename) {
  const std::size_t dot = filename.find_last_of('.');
  std::string extension = filename.substr(dot + 1);
  std::transform(
      extension.begin(), extension.end(), extension.begin(),
      [](unsigned char ch) { return static_cast<char>(::tolower(ch)); });
  if (extension == "real") {
    import(filename, Format::Real);
  } else if (extension == "qasm") {
    import(filename, Format::OpenQASM3);
  } else if (extension == "tfc") {
    import(filename, Format::TFC);
  } else if (extension == "qc") {
    import(filename, Format::QC);
  } else {
    throw QFRException("[import] extension " + extension + " not recognized");
  }
}
```

Another clue is that the probelm is in the parser bacuse this error message type is typically raised by the parser, as seen in this test in file `mqt-core/test/ir/test_qasm3_parser.cpp`:
```cpp
  TEST_F(Qasm3ParserTest, ImportQasmInvalidExpected) {
  const std::string testfile = "OPENQASM 3.0;\n"
                               "qubit[2] q;\n"
                               "cx q[0] q[1];"; // missing comma
  EXPECT_THROW(
      {
        try {
          const auto qc = QuantumComputation::fromQASM(testfile);
        } catch (const qasm3::CompilerError& e) {
          EXPECT_EQ(e.message, "Expected ',', got 'Identifier'.");
          throw;
        }
      },
      qasm3::CompilerError);
}
```

Indeed also this snippet fails:
```python
from mqt.core import QuantumComputation
qasm_string_a = """
OPENQASM 2.0;
include "qelib1.inc";
gate ms(param0) q0,q1,q2 { rxx(0.844396) q0,q1; rxx(0.844396) q0,q2; rxx(0.844396) q1,q2; }
qreg qr[3];
creg cr[3];
ms(0.844396) qr[3],qr[16],qr[22];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
"""
QuantumComputation.from_qasm(qasm_string_a)
```
Reporting the same error:
```
RuntimeError: <input>:4:6:
Expected 'Identifier', got 'ms'.
```
Suggesting the problem is in how the `ms` gate is parsed in `mqt-core/src/ir/parsers/QASM3Parser.cpp`.

Debugging I found that using a different name makes it work:
```python
OPENQASM 2.0;
include "qelib1.inc";
gate ms_test(param0) q0,q1,q2 { rxx(0.844396) q0,q1; rxx(0.844396) q0,q2; rxx(0.844396) q1,q2; }
qreg qr[3];
creg cr[3];
ms_test(0.844396) qr[3],qr[16],qr[22];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
```
Raises no error.

## Possible solution

The error is raised in the file: `mqt-core/include/mqt-core/ir/parsers/qasm3_parser/Scanner.hpp`:
```cpp
  void expect(const char expected) {
    if (ch != expected) {
      error("Expected '" + std::to_string(expected) + "', got '" + ch + "'");
    } else {
      nextCh();
    }
  }
```
So probably most probably the problem is with the name `ms` there must be a check for the name of the gate in the parser.

## Expected Behavior
I would expect the `ms` gate to be parsed correctly since it can be creates and parsed back by Qiskit as well.



## Environment
```python
import mqt.core as core
import mqt.qcec as qcec
import qiskit
# version
print("mqt.core version:", core.__version__)
print("mqt.qcec version:", qcec.__version__)
print("qiskit version:", qiskit.__version__)
# mqt.core version: 2.7.0
# mqt.qcec version: 2.7.1
# qiskit version: 1.2.0

# G++ Compiler Version: g++ (Ubuntu 9.4.0-1ubuntu1~20.04.2) 9.4.0
```
