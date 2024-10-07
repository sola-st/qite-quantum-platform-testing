Instead of generating arbitrary program use the LintQ dataset of real world programs:

# LintQ-Dataset Generator
Run this to run and retain all the running circuits in the LintQ dataset.
```shell
# test
python -m generators.lintq_generator --folder_with_py program_bank/2024_08_29__15:52__qiskit --output_folder program_bank --timeout 60
```

For the full run:
```shell
screen -S lintq_dataset_run -L -Logfile logs/lintq_dataset.log python -m generators.lintq_generator --folder_with_py program_bank/LintQ_dataset/ --output_folder program_bank --timeout 60
```

Results: unfortunately most programs are not fully runnable often because of the use of deprecated functions.