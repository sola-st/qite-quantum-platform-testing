
## Fuzz4All - Original

- Create the docker image to run fuzz4all in the docker container:
```shell
cd docker/fuzz4all
# note that you must have openai_token.txt in the same directory
cat openai_token.txt
# to have the correct permissions to write files in the docker and
# to be able to read them in the host machine
docker build --build-arg UID=$(id -u paltenmo) --build-arg GID=$(id -g paltenmo) -t qiskit_fuzz4all .
```


- To run the docker container with GPU support use:
```shell
# from the root
docker run --rm -it --runtime=nvidia --gpus all -v $(pwd)/data/fuzz4all_output:/workspace -w /app qiskit_fuzz4all bash
# make sure that the OPENAI key is available:
export OPENAI_API_KEY=$(cat /app/openai_token.txt)
# use the 4o mini model
find /app -type f -exec sed -i 's/gpt-4/gpt-4o-mini/g' {} +
# login with hugging face:
huggingface-cli login
# paste login token, then hit n to not save the token
# then start the fuzzing campaign with the following command
python Fuzz4All/fuzz.py --config config/full_run/qiskit_opt_and_qasm.yaml main_with_config --folder /workspace --batch_size 30 --model_name bigcode/starcoder2-3b --target qiskit
```

## LLM Generator - Similar to Fuzz4All

To generate programs using the LLM model, you can use the following commands:

```shell
python entry.py --config config/v012.yaml --screen
```


## Inspection of Generated Warnings



## Not equivalent - Qiskit vs Pytket (sensitivity for approximate equivalence)
File: program_bank/v012/2024_12_16__23_03__qiskit/qiskit_circuit_5q_10g_7553_24d42f_76b26a_error.json

```
The circuits are not equivalent: /workspace/qiskit_circuit_5q_10g_7553_24d42f_random_qc_pytket.qasm, /workspace/qiskit_circuit_5q_10g_7553_24d42f_random_qc_qiskit.qasm
```

We copied the file to folder `reports/v012/01/` and add the tags: `# <START_GATES>` and `# <END_GATES>` to the python file.

To rerun and minimize the program run the following command:
```shell
python -m analysis_and_reporting.ddmin_target_file --input_folder reports/v012/01 --path_to_error reports/v012/01/qiskit_circuit_5q_10g_7553_24d42f_76b26a_error.json --clue_message 'not equivalent'
```

Interesting results here:
`reports/v012/2024_12_18__14_48/analysis_output_random_qc.ipynb`

There is a random circuit with output:
```
../reports/v012/2024_12_18__14_48/qiskit_circuit_5q_10g_7553_24d42f_76b26a_error_min_random_qc_pytket.qasm
Probabilities A:  {'00000': 0.8159202125271611, '00001': 4.889070232949262e-30, '00100': 3.0608970960607044e-33, '00101': 5.754731070590801e-63, '01000': 4.4213798334893704e-30, '01001': 5.97450527819063e-60, '01100': 1.8973598733917008e-62, '01101': 3.032651963689807e-92, '10000': 0.18407978747282874, '10001': 1.2059150455866257e-30, '10100': 6.822167365573289e-34, '10101': 7.672427332805983e-64, '11000': 1.8449418315389136e-31, '11001': 4.0098811150530924e-61, '11100': 3.787117709496746e-64, '11101': 7.914039856279156e-94}
../reports/v012/2024_12_18__14_48/qiskit_circuit_5q_10g_7553_24d42f_76b26a_error_min_random_qc_qiskit.qasm
Probabilities B:  {'00000': 0.8159202125271697, '10000': 0.1840797874728298}
```

For A the most probably are 00000 and 10000, for B the most probably are 00000 and 10000. The probabilities are very close to each other.

## CS gate problem

message: `"<input>:12,0: 'cs' is not defined in this scope"`

File error: `qiskit_circuit_5q_10g_3811_4fe1d7_ac90d3_error.json`

File: `qiskit_circuit_5q_10g_3811_4fe1d7.py`


# Insights
Most cases are:
- known crash messages (found also with other methods e.g., redefined register in BQSKit or unsupported PhaseX)
- divergences with equivalent oracle that are very minimal as above
- cases where the fuzzer uses random_circuit but the seed is not fixed thus not reproducible..