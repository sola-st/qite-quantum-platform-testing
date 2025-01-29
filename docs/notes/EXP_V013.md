## Test Cases


### Where to Place them?

- In the `tests` folder, create a new folder with the name of the module you are testing.
- Preferably add the main code in the `src` folder.
- Add the test cases in the `tests` folder.

### How to Name the Test Files?

- Use the same name as the module you are testing with the prefix `test_`.

### How to Name the Test Functions?

- Use the same name as the function you are testing with the prefix `test_`.

### How to Run the Tests?

- Run the following command in the terminal:
```shell
# from root of the repository
conda activate crosspl
python -m pytest
```

### How the Environment is Setup?

1. Install conda
2. Create a new environment from file `environment_cross.yml`
```shell
conda env create -f environment_cross.yml
```

The `requirements-dev.txt` file contains the packages required for testing. It was created with the following command:
```shell
pip list --format=freeze > requirements-dev.txt
```