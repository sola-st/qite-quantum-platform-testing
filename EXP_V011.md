### Create Dataset of Circuits


#### Quick Test
Run the generator to recreate a copy of the qiskit repo, which is instrumented.
```shell
# quick test
python -m docker_circuit_fragments_miner.test_suite_inspired_generator --test_suite_path platform_repos/test_suite_example --output_path platform_repos/test_suite_example_instrumented --abs_path_to_logger_file docker_circuit_fragments_miner/self_contained_logger.py
# official run on Qiskit repo
python -m docker_circuit_fragments_miner.test_suite_inspired_generator --test_suite_path platform_repos/qiskit --output_path platform_repos/qiskit_instrumented --abs_path_to_logger_file /opt/self_contained_logger.py
```
#### Mining Process
Build the docker container that runs the whole procedure on a specific PR.
```shell
cd docker_circuit_fragments_miner
docker build --build-arg COMMIT_HASH=cb486e6a312dccfcbb4d88e8f21d93455d1ddf82 --build-arg UID=$(id -u paltenmo) --build-arg GID=$(id -g paltenmo) -t qiskit_circuit_miner .
```

Run the container, mounting the `data/circuit_fragments` directory to the container's `/opt/circuit_storage` directory.
```shell
docker run --rm -it -v $(pwd)/data/circuit_fragments:/opt/circuit_storage qiskit_circuit_miner /bin/bash
```

Once in the container: run the test suite
```shell
# check that rust is accessible to the user
rustc --version
python -m tox -epy310 -- -n test.python.compiler.test_transpiler
```

Single command to run the test suite (in screen)
```shell
screen -dmS qiskit_circuit_miner -L -Logfile mining_fragments.log bash -c "docker run --rm -it -v $(pwd)/data/circuit_fragments:/opt/circuit_storage qiskit_circuit_miner /bin/bash -c 'python -m tox -epy310 -- -n test.python.compiler.test_transpiler'"
```


**Run entire test suite on Qiskit repo**
```shell
screen -dmS qiskit_circuit_miner -L -Logfile mining_fragments_full.log bash -c "docker run --rm -it -v $(pwd)/data/circuit_fragments:/opt/circuit_storage qiskit_circuit_miner /bin/bash -c 'python -m tox -epy310'"
```

#### Inspection Process

If the conda environment uses `qiskit==1.2.1`. and `symengine==0.13.0`, the following command can be used to inspect the circuit fragments:
```shell
python docker_circuit_fragments_miner/circuit_reader/show_fragments.py --dir_with_circuits_pkl data/circuit_fragments --export_to_qasm
```
The flag `--export_to_qasm` is optional and will export the circuits to qasm files in a sister directory `data/circuit_fragments_qasm`.

Otherwise, the following steps are necessary:
Build the docker container that reads the circuit using the specific PR version:
```shell
cd docker_circuit_fragments_miner/circuit_reader
docker build --build-arg COMMIT_HASH=cb486e6a312dccfcbb4d88e8f21d93455d1ddf82 --build-arg UID=$(id -u paltenmo) --build-arg GID=$(id -g paltenmo) -t qiskit_circuit_inspector .
```

Inspect the circuit fragments
```shell
docker run --rm -it -v $(pwd)/data/circuit_fragments:/opt/circuit_storage -v $(pwd)/docker_circuit_fragments_miner/circuit_reader:/home/regularuser/scripts/ qiskit_circuit_inspector python /home/regularuser/scripts/show_fragments.py --dir_with_circuits_pkl /opt/circuit_storage
```


#### Generate Programs for Fuzzing

There are multiple strategies to generate programs for fuzzing.

**Template-Grammar Based (MorphQ-Style)**
```shell
python -m generators.morphq_like_w_oracles --prompt generators/scaffold_oracles.jinja --output_folder program_bank/v007/ --circuit_generation_strategy "random" --max_n_qubits 32 --max_n_gates 10 --max_n_programs 3
```

**Circuit-Fragments Based**
```shell
python -m generators.morphq_like_w_oracles --prompt generators/scaffold_oracles.jinja --output_folder program_bank/v007/ --circuit_generation_strategy "circuit_fragments" --seed_qasm_folder data/circuit_fragments_qasm --max_n_programs 3
```


## Possible Bugs


### Not Equivalent Circuits - Pennylane vs Pytket
```shell
program_bank/v007/2024_10_31__17_01__qiskit/qiskit_circuit_5q_10g_1_9e03e1_d56620_error.json
# continue...
```

### Not Equivalent Circuits - BQSKit vs Pytket

```shell
program_bank/v007/2024_10_31__17_24__qiskit/qiskit_circuit_5q_10g_5_92b84e_5ea2d6_error.json
# continue...
```



### Mat::at when using QCEC

program_bank/v007/2024_10_31__17_24__qiskit/qiskit_circuit_5q_10g_3_8ce198_d84698_error.json

Run to minimize the program
```shell
# reports/v001_manual/011/qiskit_circuit_5q_10g_3_8ce198_d84698_error.json
python -m analysis_and_reporting.ddmin_target_file --input_folder reports/v001_manual/011/ --path_to_error reports/v001_manual/011/qiskit_circuit_5q_10g_3_8ce198_d84698_error.json --clue_message 'map::at'
```

Rerun the program
```shell
docker run --rm -v "$(pwd)/reports/v001_manual/011/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_3_8ce198_d84698_error_min.py
```

