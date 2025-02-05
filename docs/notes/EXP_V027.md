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


## Reply Errors

To replay the results of a QITE loop on a specific error `0000005_33b7d0_50615d_error.json`, you can use:

```bash
python -m qite.qite_replay --metadata_path program_bank/v024/run006/error/0000005_33b7d0_50615d_error.json --input_folder program_bank/v024/run006 --output_debug_folder program_bank/v024/run006/debug
```


