Generate programs using MorhpQ with the latest Qiskit version.
```shell
python -m generators.morphq_like --prompt generators/morphq.jinja --output_folder program_bank --max_n_qubits 5 --max_n_gates 10 --max_n_programs 10
```


## Oracle 1: Export (analogous to basic fuzzing)
Convert the Qiskit circuits to QASM code using different platforms:
```shell
python validate/extract_qasm.py --input_folder program_bank/2024_09_23__17_19__qiskit --image_name qiskit_runner
```

## Oracle 2: Compare QASM
Compare all the pairs of QASM files with the same prefix but different suffixes.
`_pytket.qasm`, `_qiskit.qasm`, and `_pennylane.qasm` files.

```shell
# compare all platforms
python validate/compare_qasm.py --input_folder program_bank/2024_09_23__17_19__qiskit
```

## Oracle 3: Parse QASM
Try to parse all the generated qasm files using Qiskit, Pytket, and PennyLane.

```shell
# run all platforms
python -m validate.parse_qasm2 --input_folder program_bank/2024_09_23__17_19__qiskit --image_name qiskit_runner
# you can add the platform argument
#  --platform_name pennylane
#  --platform_name pytket
#  --platform_name qiskit
```


## Inspect Results

Run delta debugging on a single qasm file:
```shell
python -m analysis_and_reporting.ddmin_test
```




