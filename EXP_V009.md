## Run v004

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