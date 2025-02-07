### Kernel Crash During QCEC Circuit Comparison (Different Sized Circuits with Boundary Swap)

### Description
Running a comparison between two circuits led to a kernel crash of QCEC.

### Expected behavior
The comparison should complete without causing a kernel crash.

### How to Reproduce
1. Create two QASM files with the following content:
    - `qasm_a.qasm`:
      ```qasm
      OPENQASM 2.0;
      include "qelib1.inc";
      qreg q[1];
      rz(1) q[0];
      ```
    - `qasm_b.qasm`:
      ```qasm
      OPENQASM 2.0;
      include "qelib1.inc";
      qreg q[3];
      swap q[1],q[2];
      ```
2. Save the QASM content to files:
    ```python
    path_qasm_1 = "qasm_a.qasm"
    path_qasm_2 = "qasm_b.qasm"

    with open(path_qasm_1, 'w') as file:
        file.write(qasm_a)

    with open(path_qasm_2, 'w') as file:
        file.write(qasm_b)
    ```
3. Run the following code to verify the circuits:
    ```python
    from mqt import qcec

    result = qcec.verify(
        str(path_qasm_1),
        str(path_qasm_2),
        transform_dynamic_circuit=True)
    equivalence = str(result.equivalence)
    ```

### Additional Information
The kernel crashed while executing the code. The log has no interesting message:
```
23:38:10.947 [info] Restarted 55f0b765-eeab-41e1-a2d9-d71086dd5d5a
23:38:12.956 [error] Disposing session as kernel process died ExitCode: undefined, Reason:
```
