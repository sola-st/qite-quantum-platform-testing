Generate programs using MorhpQ with the latest Qiskit version.
Note that this will generate the python files and also run them (unlike the `morphq_like` generator).
```shell
python -m generators.morphq_like_w_oracles --prompt generators/morphq_w_oracles.jinja --output_folder program_bank --max_n_qubits 5 --max_n_gates 10 --max_n_programs 3
```


## Case A: Use Delta-Debugging to Minimize the Error-Inducing Input
Run this script to minimize the input python file in qiskit to see when we get the same error.
```shell
# example 1: parsing error
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/2024_09_25__15_12__qiskit --path_to_error program_bank/2024_09_25__15_12__qiskit/qiskit_circuit_5q_10g_1_56f829_43fca2_error.json --clue_message "'rxx' is not defined in this scope"
# example 2: QCEC error
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/2024_09_25__15_12__qiskit --path_to_error program_bank/2024_09_25__15_12__qiskit/qiskit_circuit_5q_10g_2_76cdf0_e6c9dd_error.json --clue_message "The circuits are not equivalent"
# example 3: QCEC error
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/2024_09_25__15_12__qiskit --path_to_error program_bank/2024_09_25__15_12__qiskit/qiskit_circuit_5q_10g_2_76cdf0_927acc_error.json --clue_message "The circuits are not equivalent"
```

To manually run a specific file, you can use the following command:
```shell
# example 2
docker run --rm -v "$(pwd)/program_bank/2024_09_25__15_12__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_2_76cdf0_e6c9dd_error_min.py
# example 3
docker run --rm -v "$(pwd)/program_bank/2024_09_25__15_12__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_2_76cdf0_927acc_error_min.py
```

# Manual Investigation

To run the file with a breakpoint, you can use the following command. We recommend moving the file to the `triage_cases` folder to work in a clean environment.
Note that the `-it` flag is used to keep the terminal open after the script finishes.
```shell
docker run -it --rm -v "$(pwd)/program_bank/2024_09_25__15_12__qiskit/triage_cases:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_2_76cdf0_927acc_error_min.py
```


## Useful Tips/Commands to Debug

1. Print the circuits before and after a certain modification.
```python
# qiskit
simplified_qiskit_circ.draw()
# pennylane
print(qml.draw(qml_circuit)({}))
```



## Case B: Automatically Create the Report (from errors)


### 1. Identify the Platform to Report the Error
Tun this script to generate a `target_platform.json` file that contains the target platform and reason for reporting to that platform. (INCOMPLETE, only prompt is generated so far)
```shell
python -m analysis_and_reporting.identify_platform --input_folder program_bank/2024_09_25__15_12__qiskit/ --target_circuit qiskit_circuit_5q_10g_2_76cdf0.py --target_error qiskit_circuit_5q_10g_2_76cdf0_e6c9dd_error.json --template_path analysis_and_reporting/platform_identification.jinja
```
This will generate an output file `*.triage.json` that contains the prompt for now




## Delta-Debugging + Manual Inspection

```shell
# Delta Debugging
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/2024_09_25__15_51__qiskit --path_to_error program_bank/2024_09_25__15_51__qiskit/qiskit_circuit_5q_10g_1_382efa_46e3e2_error.json --clue_message "The circuits are not equivalent"
# Run and Get Two QASM Files
docker run --rm -v "$(pwd)/program_bank/2024_09_25__15_51__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_1_382efa_46e3e2_error_min.py
# Root Cause
Pennylane wrong qubit order
```


### program_bank/2024_09_25__15_51__qiskit/qiskit_circuit_5q_10g_3_403546_10a80c_error.json

```shell
# Delta Debugging
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/2024_09_25__15_51__qiskit --path_to_error program_bank/2024_09_25__15_51__qiskit/qiskit_circuit_5q_10g_3_403546_10a80c_error.json --clue_message "Gate has an invalid number of parameters"
# Run and Get Two QASM Files
docker run --rm -v "$(pwd)/program_bank/2024_09_25__15_51__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_3_403546_10a80c_error_min.py
```