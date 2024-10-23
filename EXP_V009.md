## Run v004



### Pytket PhasedX error - Exporter with Twice Decomposition
```shell
# minimize the program
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/v004/2024_10_18__16_09__qiskit --path_to_error program_bank/v004/2024_10_18__16_09__qiskit/qiskit_circuit_32q_10g_34085_28e917_5ead57_error.json --clue_message 'Cannot print command of type: PhasedX'
```

Minimized version: `program_bank/v004/2024_10_18__16_09__qiskit/qiskit_circuit_32q_10g_34085_28e917_5ead57_error_min.py`

1. Copy the program in the report folder (easier to access):
```shell
cp program_bank/v004/2024_10_18__16_09__qiskit/qiskit_circuit_32q_10g_34085_28e917_5ead57_error_min.py reports/v001_manual/006
```

2. Rerun the program with the following command:
```shell
# rerun
docker run --rm -v "$(pwd)/reports/v001_manual/006/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_32q_10g_34085_28e917_5ead57_error_min.py
```


### RXX Gate - Unequivalent

Given the following minimized program: `../program_bank/v004/2024_10_18__16_09__sample_errors/qiskit_circuit_32q_10g_8976_aee7cb_cfbaae_error_min.py`

Run the program with the following command:
```shell
docker run --rm -v "$(pwd)/program_bank/v004/2024_10_18__16_09__sample_errors/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_32q_10g_8976_aee7cb_cfbaae_error_min.py
```

**Example 2**:
`../program_bank/v005/2024_10_22__14_17__sample_errors/qiskit_circuit_32q_10g_564_52d486_f2d8ef_error_min.py`

Run the program with the following command:
```shell
docker run --rm -v "$(pwd)/program_bank/v005/2024_10_22__14_17__sample_errors/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_32q_10g_564_52d486_f2d8ef_error_min.py
```


**Example 3**: after having excluded `equivalence_up_to_global_phase` from the comparison, the following error is raised:
`../program_bank/v005/2024_10_22__22_32__sample_errors/qiskit_circuit_32q_10g_159_29fa08_4f5c57_error_min.py`

Run the program with the following command:
```shell
docker run --rm -v "$(pwd)/program_bank/v005/2024_10_22__22_32__sample_errors/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_32q_10g_159_29fa08_4f5c57_error_min.py
```

