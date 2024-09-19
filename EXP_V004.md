Generate programs using MorhpQ with the latest Qiskit version.
```shell
python -m generators.morphq_like --prompt generators/morphq.jinja --output_folder program_bank --max_n_qubits 5 --max_n_gates 10 --max_n_programs 10
```

Run them alone to see if there is any obvious error.
```shell
python validate/retain_runnable.py --input_folder program_bank/2024_09_19__17:40__qiskit --output_folder program_bank/2024_09_19__17:40__qiskit__runnable --image_name qiskit_runner
```

Run them by adding the extraction of QASM code.
```shell
python validate/extract_qasm.py --input_folder program_bank/2024_09_19__21:19__qiskit --image_name qiskit_runner
```

Compare all the pairs of QASM files with the same prefix but different suffixes.
`_pytket.qasm` and `_qiskit.qasm` files.

```shell
python validate/compare_qasm.py --input_folder program_bank/2024_09_19__21:19__qiskit
```





## Improvement points in MorphQ generator

- Some arguments are list of qubits
```shell
Traceback (most recent call last):
File "/workspace/to_execute.py", line 14, in <module>
qc.mcp(5.930564, qr[0], qr[1], qr[3])
File "/usr/local/lib/python3.10/site-packages/qiskit/circuit/quantumcircuit.py", line 4612, in mcp
num_ctrl_qubits = len(control_qubits)
TypeError: object of type 'Qubit' has no len()

Failed to execute qiskit_circuit_5q_10g_cc1e8f_6.py
--------------------
Traceback (most recent call last):
    File "/workspace/to_execute.py", line 17, in <module>
    qc.mcry(5.12274, qr[3], qr[4], qr[2], qr[0])
    File "/usr/local/lib/python3.10/site-packages/qiskit/circuit/library/standard_gates/multi_control_rotation_gates.py", line
349, in mcry
    raise QiskitError(f"Unrecognized mode for building MCRY circuit: {mode}.")
qiskit.exceptions.QiskitError: "Unrecognized mode for building MCRY circuit: Qubit(QuantumRegister(5, 'qr'), 0)."

Failed to execute qiskit_circuit_5q_10g_d9129b_8.py
```