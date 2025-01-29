## Large Scale Generation of Programs
Generate programs using MorhpQ with the latest Qiskit version.
You can configure the parameters in the `config/v001.yaml` file.
```shell
python entry --config config/v001.yaml --screen
```
With the `--screen` flag, the task will run in the background.

## EDA Explore the Error Messages via Clustering
Open this notebook: `notebooks/001_Cluster_Error_Messages.ipynb`
You can find a clustering of the error messages to facilitate the inspection.

You can directly copy the command to run delta debugging from the output of the clustering.

## Types of Errors Found so Far

- Parsing error: `'gatename' is not defined in this scope` (Qiskit)
- QCEC error: `The circuits are not equivalent` (Pennylane - Qubit Oder)


## Tweaks to reduce false positives

- Remove `reset` (asking to enable QCEC dynamic circuit feature -`transform_dynamic_circuits=True`)
- Remove `Measure` (not supported by PennyLane QASM serializer: `Operation MidMeasureMP not supported by the QASM serializer`)
- Remove `Delay` problem when importing in Pytket (`conversion of qiskit's delay instruction is currently unsupported by qiskit_to_tk.`)


## Deep Dive Inspection

To manually run a specific file, you can use the following command:
```shell
docker run -it --rm -v "$(pwd)/program_bank/2024_09_25__15_12__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_2_76cdf0_927acc_error_min.py
```
Since we have `-it` flag, you can also add breakpoints to your minimized program.


## Useful Tips/Commands to Debug

1. Print the circuits before and after a certain modification.
```python
# qiskit
simplified_qiskit_circ.draw()
# pennylane
print(qml.draw(qml_circuit)({}))
```

# Bugs Found

### ISwap
File:
`program_bank/v001/2024_10_04__14_48__qiskit/qiskit_circuit_30q_10g_91_41ba22_a542f6_error_min.py`

```python
# rerun
docker run --rm -v "$(pwd)/program_bank/v001/2024_10_04__14_48__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_30q_10g_91_41ba22_a542f6_error_min.py
# interactive run
docker run --rm -it -v "$(pwd)/program_bank/v001/2024_10_04__14_48__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_30q_10g_91_41ba22_a542f6_error_min.py
```


## Run Number v002


## SX Gate: Pytket vs Qiskit

Minimized File: `program_bank/v002/2024_10_07__17_03__qiskit/qiskit_circuit_30q_10g_1257_47ef88_4ff963_error_min.py`

Rerun:
```shell
docker run --rm -v "$(pwd)/program_bank/v002/2024_10_07__17_03__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_30q_10g_1257_47ef88_4ff963_error_min.py
```

After inspection they are equivalent up to a global phase and the difference is due to the `qc.decompose()` in Qiskit which makes stronger assumptions.

## MS Gate: PennyLane vs Qiskit: Cannot import second circuit

Minimized File: `program_bank/v002/2024_10_07__17_03__qiskit/qiskit_circuit_30q_10g_257_564c6c_9a9f86_error_min.py`

Rerun:
```shell
docker run --rm -v "$(pwd)/program_bank/v002/2024_10_07__17_03__qiskit:/workspace" -w /workspace qiskit_runner python qiskit_circuit_30q_10g_257_564c6c_9a9f86_error_min.py
```