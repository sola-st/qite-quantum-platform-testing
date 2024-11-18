## Bug Triaging

# Step 1: Explore the Errors

Explore which errors are present in the error reports using the notebook `004_003_Cluster_Error_Messages.ipynb`.

This will create a new folder with a sample of errors to explore.


# Step 2: Minimize all the Files

WARNING: to do this step you need to know which is the fixed part of the error message that you want to keep when using the ddmin algorithm.

By default we assume we deal with not equivalent programs, so we keep the error message that says `not equivalent`.

```shell
# this can be done with the same notebook or manually with
python -m analysis_and_reporting.ddmin_target_file --input_folder reports/v001_manual/009/ --path_to_error reports/v001_manual/009/qiskit_circuit_32q_10g_10888_254ab7_b114cb_error.json --clue_message 'ryy'
```

# Step 3: Rerun the Minimized Files

```shell
docker run --rm -v "$(pwd)/reports/v001_manual/009/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_32q_10g_10888_254ab7_b114cb_error_min.py
```
This will generate QASM in the folder with the error.


# Step 2-3 Together

```shell
# via command line
python -m analysis_and_reporting.triage --path_error_json program_bank/v007/2024_10_31__17_51__qiskit/qiskit_circuit_5q_10g_9_160f04_cfe9f1_error.json --parent_report_folder reports/v008 --clue_message 'not equivalent'
```


## Some Domain-Specific Question to Ask

**Observation**:
Sometimes executing the circuits with all zeros as input gives the same output by chance.
**Question**:
Is there any simple input where only one bit is initialized to 1 (e.g. on the control line of a CNOT gate)? Is that giving a different output?


# Interesting Buggy Programs

## QCEC - Partial equivalence checking

`reports/v008/2024_11_12__14_05/analysis_output.ipynb`

Message:
```
[QCEC] Warning: at least one of the circuits has garbage qubits, but partial equivalence checking is turned off. In order to take into account the garbage qubits, enable partial equivalence checking. Consult the documentation for moreinformation.
```


## Pennylane measures all the qubits by default

`reports/v008/2024_11_12__14_07/analysis_output.ipynb`

Message:
```
QCEC result: not_equivalent


q_0: ──────────────────
     ┌─┐
q_1: ┤M├───────────────
     └╥┘
q_2: ─╫────────────────
      ║ ┌─────────────┐
q_3: ─╫─┤ U3(π/2,0,π) ├
      ║ └─────────────┘
q_4: ─╫────────────────
      ║
q_5: ─╫────────────────
      ║
c: 4/═╩════════════════
      0
     ┌───┐               ┌─┐
q_0: ┤ I ├───────────────┤M├────────────
     ├───┤               └╥┘┌─┐
q_1: ┤ I ├────────────────╫─┤M├─────────
     ├───┤                ║ └╥┘┌─┐
q_2: ┤ I ├────────────────╫──╫─┤M├──────
     ├───┤┌─────────────┐ ║  ║ └╥┘   ┌─┐
q_3: ┤ I ├┤ U3(π/2,0,π) ├─╫──╫──╫────┤M├
     ├───┤└─────┬─┬─────┘ ║  ║  ║    └╥┘
q_4: ┤ I ├──────┤M├───────╫──╫──╫─────╫─
     ├───┤      └╥┘       ║  ║  ║ ┌─┐ ║
q_5: ┤ I ├───────╫────────╫──╫──╫─┤M├─╫─
     └───┘       ║        ║  ║  ║ └╥┘ ║
c: 6/════════════╩════════╩══╩══╩══╩══╩═
                 4        0  1  2  5  3

```

## Not Reproducible QCEC errors

`reports/v008/2024_11_12__14_29/qiskit_circuit_5q_10g_4250_3f1a07.py`

Run the base program again to observe qasm
```shell
# rerun
docker run --rm -v "$(pwd)/reports/v008/2024_11_12__14_29/:/workspace" -w /workspace qiskit_runner python qiskit_circuit_5q_10g_4250_3f1a07.py
```