## Debugging Session


### Pennylane - merge rotations
program_bank/v026_iter_5/2025_02_13__17_27/minimize_comparison/0000671_b097d0_debug

### Pytket - Error during extraction from ZX diagram: diagram does not have gflow

Similar of https://github.com/CQCL/tket/issues/1566
program_bank/v026_iter_5/2025_02_08__01_56/minimized/0001574_qite_a59183.qasm

# Pytket - KAK

in pytket_optimizer_kak_decomposition.
Cannot obtain matrix from op: CustomGate
../program_bank/v026_iter_2/2025_02_13__17_26/error/0002521_ec8d79_17eb06_error.json

To minimize with delta debugging:
```bash
python -m qite.delta_debugging --error_json program_bank/v026_iter_2/2025_02_13__17_26/error/0002521_ec8d79_17eb06_error.json --output_folder program_bank/v026_iter_2/2025_02_13__17_26/minimized --input_folder program_bank/v026_iter_2/2025_02_13__17_26
```

Minimized:
program_bank/v026_iter_2/2025_02_13__17_26/minimized/0002521_ec8d79.qasm


# Pytket - Full Peephole (transient failure - not reproducible)

../program_bank/v026_iter_2/2025_02_13__19_07/error/0004886_d92325_2b6f44_error.json

To minimize with delta debugging:
```bash
python -m qite.delta_debugging --error_json program_bank/v026_iter_2/2025_02_13__19_07/error/0004886_d92325_2b6f44_error.json --output_folder program_bank/v026_iter_2/2025_02_13__19_07/minimized --input_folder program_bank/v026_iter_2/2025_02_13__19_07
```


# BQSKit missing u0 definition

message: `Expected 0 params got 1 params for gate u0.`


program_bank/v037/2025_02_20__23_37/error/0000427_01efa7_de7ee3_error.json

https://github.com/BQSKit/bqskit/blob/8651d8dcd003959a76be613c9d14db65b6f37a91/bqskit/ir/lang/qasm2/visitor.py#L228