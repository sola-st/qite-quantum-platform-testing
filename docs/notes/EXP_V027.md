# QITE Workflow


## Fyzzing

To run the program generator in QASM you can use:

```bash
python -m generators.qasm_code_gen --num_qubits 11 --num_gates 15 --num_programs 3 --output_dir program_bank/v024/run006
```

Then to run the QITE algorithm on the generated programs you can use:

```bash
python -m validate.qite_loop --input_folder program_bank/v024/run006 --number_of_rounds 1
```

This can be done jointly by running:

```bash
python entry.py --config config/v024.yaml
```

The results will be stored in the output folder specified in the config file.
Typically the folder will have a structure like this:

```
output_folder
│
└───metadata
│   └─── 0000010_qite_e98ef5.json  # <-- if the QITE loop was run successfully
│
└───errors
│   └─── 0000001_465cfb_0123f5_error.json  # <-- if the QITE loop failed
│   └─── 0000002_3e7836_41010a_error.json
|   ...
│
└─── 0000001_465cfb.qasm
└─── 0000002_465cfb.qasm
...
```

## Explore Errors

To explore the errors found by the QITE loop you can use:

```bash
python -m qite.explore_warnings --folder_path program_bank/v024/2025_02_05__23_59/error --top_k 3
```


## Reply Errors

To replay the results of a QITE loop on a specific error `0000005_33b7d0_50615d_error.json`, you can use:

```bash
python -m qite.qite_replay --metadata_path program_bank/v024/run006/error/0000005_33b7d0_50615d_error.json --input_folder program_bank/v024/run006 --output_debug_folder program_bank/v024/run006/debug
```

```
python -m qite.qite_replay --metadata_path program_bank/v024/2025_02_05__17_57/error/0000012_109bc1_65b230_error.json --input_folder program_bank/v024/2025_02_05__17_57 --output_debug_folder program_bank/v024/2025_02_05__17_57/debug
```

To minimize the error run this command:

```bash
python -m qite.delta_debugging --error_json program_bank/v024/2025_02_05__17_57/error/0000012_109bc1_65b230_error.json --output_folder program_bank/v024/2025_02_05__17_57/minimized --input_folder program_bank/v024/2025_02_05__17_57
```

## Comparison of QASM

To compare two QASM files you can use:

```bash
python -m qite.spot_divergences --input_folder program_bank/v025/2025_02_07__19_47 --comparison_folder program_bank/v025/2025_02_07__19_47/comparison --metadata_folder program_bank/v025/2025_02_07__19_47/metadata
```

This will generate the folder `comparison` with the divergences found between the two QASM files.

## Explore Warnings

To explore the warnings found by the QITE loop you can use:

```bash
python -m qite.explore_warnings --folder_path program_bank/v025/2025_02_07__19_47/comparison --top_k 10 --target_field 'equivalence'
```
You can select one of the categories and it will prompt you to the delta debugging of that tool. It will generate a folder with the minimized version of the QASM file and the graph of equivalences.

To run the delta debugger alone you can use:

```bash
python -m qite.delta_debugging_comparison --comparison_metadata program_bank/v024/2025_02_06__17_14/comparison/0000009_qite_88e429_vs_0000009_qite_b6cb8e.json --input_folder program_bank/v024/2025_02_06__17_14 --output_folder program_bank/v024/2025_02_06__17_14/minimize_comparison
```
