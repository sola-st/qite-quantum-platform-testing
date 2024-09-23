Generate programs using MorhpQ with the latest Qiskit version.
```shell
python -m generators.morphq_like --prompt generators/morphq.jinja --output_folder program_bank --max_n_qubits 5 --max_n_gates 10 --max_n_programs 10
```

Convert the Qiskit circuits to QASM code using different platforms:
```shell
python validate/extract_qasm.py --input_folder program_bank/2024_09_23__17_19__qiskit --image_name qiskit_runner
```
