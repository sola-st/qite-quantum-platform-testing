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
python3 -m slipcover --json --out my_coverage.json --source generators --source /home/paltenmo/.conda/envs/crosspl/lib/python3.10/site-packages/qiskit python tests/generators/test_combine_circuits.py
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
