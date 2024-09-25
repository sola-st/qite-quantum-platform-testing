Generate programs using MorhpQ with the latest Qiskit version.
Note that this will generate the python files and also run them (unlike the `morphq_like` generator).
```shell
python -m generators.morphq_like_w_oracles --prompt generators/morphq_w_oracles.jinja --output_folder program_bank --max_n_qubits 5 --max_n_gates 10 --max_n_programs 3
```


## Use Delta-Debugging to Minimize the Error-Inducing Input
Run this script to minimize the input python file in qiskit to see when we get the same error.
```shell
# example 1: parsing error
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/2024_09_25__15_12__qiskit --path_to_error program_bank/2024_09_25__15_12__qiskit/qiskit_circuit_5q_10g_1_56f829_43fca2_error.json --clue_message "'rxx' is not defined in this scope"
# example 2: QCEC error
python -m analysis_and_reporting.ddmin_target_file --input_folder program_bank/2024_09_25__15_12__qiskit --path_to_error program_bank/2024_09_25__15_12__qiskit/qiskit_circuit_5q_10g_2_76cdf0_e6c9dd_error.json --clue_message "The circuits are not equivalent"
```

To manually run a specific file, you can use the following command:
```shell
docker run --rm -v "$(pwd)/program_bank/2024_09_25__15_12__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_2_76cdf0_e6c9dd_error_min.py
```