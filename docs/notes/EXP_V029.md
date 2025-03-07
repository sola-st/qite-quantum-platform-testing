# Coverage Computation

This includes both:
- Python coverage using `coverage.py` for all platforms
- Rust coverage using `llvm-cov` for qiskit
- C++ coverage using `gcovr` for tket

1. Create a new config file e.g. `config/v041.yaml` as usual.


2. Run the following commands to fun the fuzzing

```shell
# from repo
bash docker/coverage_toolkit/run_qite_in_docker.sh -c config/v042.yaml
```

3. Check the resulting `.xml` files in the corresponding folder in the `program_bank` folder.

```shell
ls -l program_bank/v042/<RUN FOLDER>/*.xml
```


4. To run all the coverage you can use the following command

```shell
screen bash docker/coverage_toolkit/run_qite_in_docker.sh -c config/v045.yaml --interactive
## interactive allows to use CTRL + C to stop the process
## screen is for running in the background
## it should also produce a log in the logs folder
```

5. To compute the coverage files manually you can use the following commands

```shell
python -m qite.compute_coverage --folder_path program_bank/v046_debug/2025_03_07__16_29
```
This is usually done automatically when running the `run_qite_in_docker.sh` script.

Note: This command is useful to get the coverage data from the MorphQ run in a analogous and comparable way.
```shell
python -m qite.compute_coverage --folder_path path/to/MorphQ-Quantum-Qiskit-Testing-ICSE-23/data/qmt_v14
```

# Problems

llvm-profdata uses a difernt llvm thatn what used by rust


```shell
rustc --version --verbose
# vs
llvm-profdata --version
```

## Solution

```shell
$(rustc --print sysroot)/lib/rustlib/x86_64-unknown-linux-gnu/bin/llvm-profdata --version

# this uses the same llvm as rust


# OPTION

# download another llvm-profdata e.g. that reads the old format version
apt-get install -y llvm-16
```

