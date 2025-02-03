# Run v023 - Chained Translation


## Coverage Computation

To run the computation of the coverage of one program use:

```bash
screen -S coverage_v023 python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v023/2025_01_30__15_27__qiskit --output_folder data/coverage/v023_four_platforms --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket --timeout 120 --number_of_programs 1
```

Inspect them with the notebook `013`.

```bash
# program_bank/v023/2025_01_30__11_54__qiskit
screen -S coverage_v023 python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v023/2025_01_30__11_54__qiskit --output_folder data/coverage/v023_four_platforms_1000 --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket --timeout 120 --number_of_programs 100 --n_processes 4
```

