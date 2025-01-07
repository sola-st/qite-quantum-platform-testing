# Cross-Optimization Oracle

To run the cross-optimization oracle, you have to select a different prompt template: `generators/scaffold_multiple_oracles.jinja`.

Run this command with the respective configuration file:

```bash
python entry.py --config config/v015.yaml --screen
```

## Coverage Computation
To compute the coverage use the following command:
```bash
screen -S coverage_v015 python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v015/2024_12_31__15_38__qiskit --output_folder data/coverage/v015_four_platforms --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket --timeout 120 --number_of_programs 100
```


# Interesting Warnings

# program_bank/v015/2024_12_30__15_33__qiskit/qiskit_circuit_15q_30g_2_104aba_009e0e_error.json




# Debug
After running the coverage computation it seems that all the runs end up in timeout... So I try running a single circuit with docker to add breakpoints and debug the issue.

```bash
docker run --rm -it -v $(pwd)/experiments/debug_cross_optimization/qiskit_circuit_15q_30g_1000_11c341.py:/workspace/to_execute.py qiskit_runner python /workspace/to_execute.py
```

- Possible cause: optimize_with_bqskit running indefinitely
- Solution: disable that function and rerun

```bash
python entry.py --config config/v015.yaml --screen
# output in : program_bank/v015/2025_01_07__14_51__qiskit
# run the coverage with the new output
screen -S coverage_v015 python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v015/2025_01_07__14_51__qiskit --output_folder data/coverage/v015_four_platforms_no_bqskit --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket --timeout 30 --number_of_programs 30
```
