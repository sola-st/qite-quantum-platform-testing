# Cross-Optimization Oracle

To run the cross-optimization oracle, you have to select a different prompt template: `generators/scaffold_multiple_oracles.jinja`.

Run this command with the respective configuration file:

```bash
python entry.py --config config/v015.yaml --screen
```

## Coverage Computation
To compute the coverage use the following command:
```bash
python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v015/2024_12_31__15_38__qiskit --output_folder data/coverage/v015_four_platforms --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket --timeout 60 --number_of_programs 3 --n_processes 4
```


# Interesting Warnings

# program_bank/v015/2024_12_30__15_33__qiskit/qiskit_circuit_15q_30g_2_104aba_009e0e_error.json


