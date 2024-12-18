# Comparing the Stitching Strategy vs Random

# Random
Randomly generate quantum circuits picking from a list of gates and apply them to a single unique register.


To run it use the following command:
```bash
python entry.py --config config/v010.yaml --screen
```
Use this to see the progress in terms of the number of circuits generated.
```bash
cd program_bank/v010/2024_11_25__13_55__qiskit  # <--- your folder
ls *.py | wc -l
```

To compute the coverage use the following command:
```bash
To compute the coverage use the following command:
```bash
python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v010/2024_11_25__13_55__qiskit --output_folder data/coverage/v010_four_platforms --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket --timeout 30 --number_of_programs 3
```

To merge them:
```bash
python3 -m slipcover --merge data/coverage/v010_four_platforms/coverage_reports/*.json --out data/coverage/v010_four_platforms/merged_coverage.json
```



# Stitching Strategy
Use the SPIU strategies to compose two circuits:
- S: Sequential
- P: Parallel
- I: Interleaved
- U: Unitary injection

