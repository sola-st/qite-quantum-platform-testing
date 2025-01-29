# To run Circuit Knitting

1. Run the following command in the terminal:
```shell
python -m generators.combine_circuits --input_folder tests/artifacts/pickled_quantum_circuits --output_folder program_bank/circuit_stitching --seed 42
```
This will generate only a new circuit.


## Fuzzing with the new combined circuits

Run the new generation of the circuits at scale:
```shell
python -m generators.morphq_like_w_oracles --output_folder="data/circuit_sequential_combination_v001" --prompt="generators/scaffold_oracles.jinja" --circuit_generation_strategy="sequential_knitting" --max_n_programs=3 --seed=42 --seed_program_folder="data/circuit_fragments"
```