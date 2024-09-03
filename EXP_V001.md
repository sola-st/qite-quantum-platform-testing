Steps:

- Download Qiskit platform repo locally
```shell
cd platform_repos/
git clone https://github.com/Qiskit/qiskit.git
```
- Extract the api used in it with:
```shell
python scan_functions.py --path_to_local_folder platform_repos/qiskit/ --output_path available_apis/qiskit
```

- Generate Qiskit programs
```shell
# LOCAL GPUs
python generators/mono_program_generator.py --platform qiskit --path_api_names available_apis/qiskit.json --prompt generators/mono_program_generator.jinja
# GROQ CLOUD
python generators/mono_program_generator_groq.py --platform qiskit --path_api_names available_apis/qiskit.json --prompt generators/mono_program_generator.jinja
```

- Extract the valid programs from it:
```shell
python validate/extract_valid_circuit_programs.py --input_folder program_bank/2024_08_29__11_44__qiskit --output_folder program_bank/2024_08_29__11_44__qiskit__valid
```

- IDEA: use docker with qiskit to run the program and see if it prints the CANARY string in stdout, if yes there are circuit to extract.

- Create the docker image to run the unsafe generated programs:
```shell
cd docker
docker build -t qiskit_runner .
```

- Create the docker image to run the unsafe generated programs:
```shell
cd docker_legacy
docker build -t qiskit_runner_legacy .
```

- Extract the programs that are runnable:
```shell
python validate/retain_runnable.py --input_folder program_bank/2024_08_29__15:52__qiskit__valid --output_folder program_bank/2024_08_29__15:52__qiskit__runnable
```
