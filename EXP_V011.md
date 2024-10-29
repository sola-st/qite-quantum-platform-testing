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
docker build --build-arg PR_NUMBER=13370 --build-arg UID=$(id -u paltenmo) --build-arg GID=$(id -g paltenmo) -t qiskit_circuit_miner .
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


#### Inspection Process

Build the docker container that reads the circuit using the specific PR version:
```shell
cd docker_circuit_fragments_miner/circuit_reader
docker build --build-arg PR_NUMBER=13370 --build-arg UID=$(id -u paltenmo) --build-arg GID=$(id -g paltenmo) -t qiskit_circuit_inspector .
```

Inspect the circuit fragments
```shell
docker run --rm -it -v $(pwd)/data/circuit_fragments:/opt/circuit_storage -v $(pwd)/docker_circuit_fragments_miner/circuit_reader:/home/regularuser/scripts/ qiskit_circuit_inspector python /home/regularuser/scripts/show_fragments.py --dir_with_circuits_pkl /opt/circuit_storage
```