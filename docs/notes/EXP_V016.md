## Explore Potential Errors


### QCEC - QASM with register size 0
`program_bank/v009/2024_11_18__21_05__qiskit/qiskit_circuit_5q_10g_6_6f76b4.py`

```
OPENQASM 2.0;
include "qelib1.inc";
qreg reg_qreg[5];
creg reg_creg[0];
h reg_qreg[0];
tdg reg_qreg[1];
h reg_qreg[1];
cx reg_qreg[0],reg_qreg[1];
z reg_qreg[0];
cx reg_qreg[2],reg_qreg[1];
cx reg_qreg[0],reg_qreg[1];
cx reg_qreg[4],reg_qreg[3];
cx reg_qreg[2],reg_qreg[3];
cx reg_qreg[2],reg_qreg[1];
z reg_qreg[4];
cx reg_qreg[4],reg_qreg[3];
cx reg_qreg[2],reg_qreg[3];
cx reg_qreg[3],reg_qreg[2];
```

### fixes / noise to suppress
- pennylane always measures all qubits
- QCEC cannot handle empty registers `Could not import second circuit: [addClassicalRegister] New register size must be larger than 0`
