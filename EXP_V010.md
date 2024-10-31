## Run v006 - BQSKit

### 'DaggerGate' object has no attribute '_qasm_name'
Given the error at path `../program_bank/v006/2024_10_28__16_56__qiskit/qiskit_circuit_32q_10g_11_40ae63_6cb0d6_error.json`

Minimize the program with the following command:
```shell
# minimize the program
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/v006/2024_10_28__16_56__qiskit --path_to_error program_bank/v006/2024_10_28__16_56__qiskit/qiskit_circuit_32q_10g_11_40ae63_6cb0d6_error.json --clue_message 'DaggerGate'
```

Rerun the minimized again with the following command:
```shell
# file located here
reports/v001_manual/008/qiskit_circuit_32q_10g_11_40ae63_6cb0d6_error_min.py
# rerun
docker run --rm -v "$(pwd)/reports/v001_manual/008/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_32q_10g_11_40ae63_6cb0d6_error_min.py
```


### RYY - Cannot parse gate of type: ryy\nLine:58 PyTket

Given the error at path `../program_bank/v006/2024_10_28__17_56__qiskit/qiskit_circuit_32q_10g_10888_254ab7_b114cb_error.json`

Minimize the program with the following command:
```shell
# minimize the program
python -m analysis_and_reporting.ddmin_target_file --input_folder reports/v001_manual/009/ --path_to_error reports/v001_manual/009/qiskit_circuit_32q_10g_10888_254ab7_b114cb_error.json --clue_message 'ryy'
```

Rerun the minimized again with the following command:
```shell
# file located here
reports/v001_manual/009/qiskit_circuit_32q_10g_10888_254ab7_b114cb_error_min.py
# rerun
docker run --rm -v "$(pwd)/reports/v001_manual/009/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_32q_10g_10888_254ab7_b114cb_error_min.py
```



### CR register - 'cr' is already defined

```python
program_bank/v006/2024_10_28__16_56__qiskit/qiskit_circuit_32q_10g_55_d0804b_936b26_error.json
```
Probably the same as below, but raised but a different platform reading the qasm file.

### CR register - register redeclared: cr

Given the error at path `program_bank/v006/2024_10_28__16_56__qiskit/qiskit_circuit_32q_10g_57_bd88ff_7182c3_error.json`.

Minimize the program with the following command:
```shell
# minimize the program
python -m analysis_and_reporting.ddmin_target_file --input_folder reports/v001_manual/010/ --path_to_error reports/v001_manual/010/qiskit_circuit_32q_10g_57_bd88ff_7182c3_error.json --clue_message 'Classical register redeclared: cr.'
```