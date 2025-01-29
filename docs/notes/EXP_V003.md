Goal: generate programs that use the latest Qiskit version appropriately.

## Idea with LMQL:
on the fly library code generation:
1. generate one line
2. run it via `exec()`
3. check if it works
4. if it works
    - (yes) proceed
    - (no) re-run the previous lines and add a comment to generate something
    different than the crashing line (report the line)
5. if the line runs successfully, add the snippet so far to the successful snippets
6. inspect the global and local variables, pick a random one, add its fields to the prompt as comment and then ask the model to use it in the next line
7. repeat from step 1

- Generate Qiskit programs
```shell
# start the model
screen lmql serve-model unsloth/Meta-Llama-3.1-8B-bnb-4bit --cuda --port 8095 --trust_remote_code True
# LOCAL GPUs - LMQL
python generators/mono_program_generator_lmql.py --platform qiskit --path_api_names available_apis/qiskit.json --prompt generators/mono_program_generator.lmql
```



## Challenge: How to generate functions?
- functions are difficult to execute line by line until they are called,
- we can do the same generation but with a function signature where we execute with an example input circuit and ask to return another circuit
```python
def new_function(circuit: QuantumCircuit) -> QuantumCircuit:
    # generate code here and execute it
    # using circuit = QuantumCircuit(5, 5)
    return new_circuit
```

## Challenge: How to run it securely and resume the computation when it crashes?
- use a docker container to run the code `exec_in_docker(code: str) -> Tuple[Optional[str], Optional[str]]`
- cache the program state (check `os.fork()` api)
https://python-course.eu/applications-python/forks-and-forking.php