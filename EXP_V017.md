## Compute Coverage

To see the doc:
```shell
python3 -m slipcover --help
```

Using the tool SlipCover, use the following command:

```shell
pip install slipcover
python3 -m slipcover -m pytest tests/generators/test_combine_circuits.py
```
This will run the test file `test_combine_circuits.py` and generate a coverage report in the standard output.
If you want to save the coverage report to a file use this command:

```bash
python3 -m slipcover --json --out my_coverage.json -m pytest tests/generators/test_combine_circuits.py
```

To collect coverage of a specific folder use the source flag:

```bash
python3 -m slipcover --json --out my_coverage.json --source generators,/home/paltenmo/.conda/envs/crosspl/lib/python3.10/site-packages/qiskit -m pytest tests/generators/test_combine_circuits.py
```

This is the format:
```json
{
    "meta": {
        "software": "slipcover",
        "version": "1.0.15",
        "timestamp": "2024-11-20T19:06:37.662122",
        "branch_coverage": false,
        "show_contexts": false
    },
    "files": {
        "tests/generators/test_combine_circuits.py": {
            "executed_lines": [
                1,
                2,
                3,
                5,
                6,
                7,
                8,
                9,
                12,
                17,
                ...,
                82,
                83,
                85
            ],
            "missing_lines": [
                86
            ],
            "summary": {
                "covered_lines": 50,
                "missing_lines": 1,
                "percent_covered": 98.03921568627452
            }
        },
        "generators/combine_circuits.py": {
            "executed_lines": [
                1,
                2,
                3,
                4,
                ...,
                146,
                172
            ],
            "missing_lines": [
                59,
                64,
                65,
                73,
                74,
                75,
                76,
                129,
                ...,
                173
            ],
            "summary": {
                "covered_lines": 47,
                "missing_lines": 30,
                "percent_covered": 61.03896103896104
            }
        }
    },
    "summary": {
        "covered_lines": 97,
        "missing_lines": 31,
        "percent_covered": 75.78125
    }
}
```

## Compare Random Generator vs SPIU (knitting)

- random generator: v010
- SPIU: v011



## Compute Coverage of a Run

To compute the coverage of a run, you can use the following command:

```bash
python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v009/2024_11_21__16_03__qiskit --output_folder data/coverage/v009 --packages /usr/local/lib/python3.10/site-packages/qiskit/circuit --packages /usr/local/lib/python3.10/site-packages/pennylane  --timeout 30 --number_of_programs 10
```

This will produce json files in the subfolder `coverage_reports` of the output folder. To merge them use
the following command:

```bash
python3 -m slipcover --merge data/coverage/v009/coverage_reports/*.json --out data/coverage/v009/merged_coverage.json
```


To compute all packages:
```bash
python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v009/2024_11_21__16_03__qiskit --output_folder data/coverage/v009_four_platforms --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket  --timeout 30 --number_of_programs 10
```

To merge them:
```bash
python3 -m slipcover --merge data/coverage/v009_four_platforms/coverage_reports/*.json --out data/coverage/v009_four_platforms/merged_coverage.json
```


# program_bank/v011/2024_11_28__18_51__qiskit

To compute the coverage (with screen):

```bash
screen -S coverage_v011 -L -Logfile logs/coverage_v011.log python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v011/2024_11_28__18_51__qiskit --output_folder data/coverage/v011_four_platforms --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket  --timeout 30 --number_of_programs 10000
```


# Observations: Many Programs Timeout

Possible reasons:
- the coverage overhead pushes the execution time of the programs over the timeout >> increase the timeout
- compute the timeout statistics with high timeout: 100 programs with 200 seconds timeout

### Collect Timeout Statistics
```bash
# random v010
screen -S coverage_v010 -L -Logfile logs/coverage_v010_stats.log python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v010/2024_11_25__13_55__qiskit --output_folder data/coverage/v010_stats --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket  --timeout 200 --number_of_programs 30

# merge
python3 -m slipcover --merge $(find data/coverage/v010_stats/coverage_reports -name "*.json" | grep -v "_time.json" | grep -v "_error.json") --out data/coverage/v010_stats/merged_coverage.json

# SPIU v011
screen -S coverage_v011 -L -Logfile logs/coverage_v011_stats.log python -m analysis_and_reporting.coverage_computation --input_folder program_bank/v011/2024_11_28__18_51__qiskit --output_folder data/coverage/v011_stats --packages /usr/local/lib/python3.10/site-packages/qiskit --packages /usr/local/lib/python3.10/site-packages/pennylane --packages /usr/local/lib/python3.10/site-packages/bqskit --packages /usr/local/lib/python3.10/site-packages/pytket  --timeout 200 --number_of_programs 30

# merge
python3 -m slipcover --merge $(find data/coverage/v011_stats/coverage_reports -name "*.json" | grep -v "_time.json" | grep -v "_error.json") --out data/coverage/v011_stats/merged_coverage.json

```