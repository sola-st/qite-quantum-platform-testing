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



# LLM Generation
LLM generated programs

To run in parallel with 4 processes use the following command:
```bash
python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v012/2024_12_16__23_03__qiskit --output_folder data/coverage/v012_four_platforms --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket --timeout 30 --number_of_programs 1000 --n_processes 4
```


# Stitching Strategy
Use the SPIU strategies to compose two circuits:
- S: Sequential
- P: Parallel
- I: Interleaved
- U: Unitary injection


```bash
screen -S coverage_v011_spiu python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v011/2024_11_28__18_51__qiskit --output_folder data/coverage/v011_four_platform_parallel_1000 --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket  --timeout 30 --number_of_programs 1000 --n_processes 4
```


# Fast Coverage Computation

To run a faster coverage computation we use the following observations:
- we run multiple programs and output their coverage in a single report (e.g. 50 programs)
- we disable the oracle QCEC before running since it does not contribute to platform coverage


To use slipcover to consider multiple files useL
```bash
python -m slipcover --json --out import_qiskit.json --source /home/paltenmo/.conda/envs/crosspl/lib/python3.10/site-packages/qiskit,/home/paltenmo/.conda/envs/crosspl/lib/python3.10/site-packages/pennylane -m pytest import_qiskit.py import_pennylane.py
# NOT WORKING: not possible
```