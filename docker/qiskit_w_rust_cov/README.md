## Build the Docker

```bash
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t qiskit_w_rust .
```

## Run the Docker

```bash
docker run -it --rm -v $(pwd)/container_accessible_folder:/home/regularuser/host qiskit_w_rust /bin/bash
```

cargo llvm-cov show-env --export-prefix
# press yes
source <(cargo llvm-cov show-env --export-prefix -y)
export CARGO_TARGET_DIR=$CARGO_LLVM_COV_TARGET_DIR
export CARGO_INCREMENTAL=1

# With these environment variables set up, we are ready to run the coverage measurements.

cargo llvm-cov clean --workspace
cargo test
uv run -- maturin develop --uv
uv run -- pytest tests --cov=foobar --cov-report xml
cargo llvm-cov report --lcov --output-path coverage.lcov

```

## Attempt 1

``` shell
python -m venv .venv
source .venv/bin/activate
pip install maturin
cd crates/accelerate
python -m maturin develop  # cal this from a folder with Cargo.toml which has [Package] field]
```

## Attempt 2

``` shell

pip install setuptools-rust
export CARGO_INCREMENTAL=0
export RUSTFLAGS="-Cinstrument-coverage"
export LLVM_PROFILE_FILE="qiskit-%p-%m.profraw"
python setup.py build_rust --inplace --debug

# run coverage
grcov . --binary-path target/debug/ --source-dir . --output-type cobertura-pretty --output-path rust.xml --llvm --branch --parallel --keep-only 'crates/*'

pip install coverage
python -m coverage run base_qc_w_opt.py && python -m coverage xml

# check if any .rs file is in the coverage report
grep -r "filename=\".*\.rs\"" coverage.xml
grep '.rs' coverage.xml | sed 's/^[ \t]*//'
```


Discussion on maturin not supporting workspaces (used instead by Qiskit)
https://github.com/PyO3/maturin/issues/291

## Attempt 3

``` shell

source .venv/bin/activate
# build single packages
python -m maturin develop -m ./crates/accelerate/Cargo.toml
# python -m maturin develop -m ./crates/pyext/Cargo.toml
# python -m maturin develop -m ./crates/qasm3/Cargo.toml
# python -m maturin develop -m ./crates/circuit/Cargo.toml
# python -m maturin develop -m ./crates/qasm2/Cargo.toml

python -m pip install pytest pytest-cov
# following https://github.com/Qiskit/qiskit/blob/7dd853da063fdb0430c5eb56627d2c0f27659821/tools/run_cargo_test.py#L37
export LD_LIBRARY_PATH="/usr/local/lib"

python -m pytest base_qc_w_opt.py --cov=qiskit --cov-report xml

```


## Attempt 4 - Working

``` shell
# cargo install rustfilt
# rm qiskit-*.profraw
# source .venv/bin/activate
# pip install lcov_cobertura
python base_qc_w_opt.py

llvm-profdata merge -sparse qiskit-*.profraw -o my_program.profdata

# to convert the mangled names to human-readable names


# OPTIONAL
llvm-cov show -Xdemangler=rustfilt  target/debug/libqiskit_pyext.so \
    -instr-profile=my_program.profdata \
    -show-line-counts-or-regions \
    -show-instantiations \
    -name=circuit


llvm-cov export -Xdemangler=rustfilt target/debug/libqiskit_pyext.so --instr-profile=my_program.profdata --format=lcov --ignore-filename-regex='^(?!crates).*$' > coverage.lcov

# to convert the lcov file to xml
lcov_cobertura -e '^(?!crates).*$' coverage.lcov -o coverage.xml

```


# Scenarios to Test

### Scenario 1: Python File Location and Coverage

*   **Hypothesis:** Running a Python file from any location within the Docker container will still result in `.profraw` files being stored in the expected Qiskit folder.
*   **Test:**
    1.  Create a simple Python script (e.g., `test.py`) that imports a Qiskit module.
    2.  Place this script in a location outside the main Qiskit directory (e.g., `/tmp`).
    3.  Run the script with the necessary environment variables set for coverage collection: `python /tmp/test.py`.
    4.  Check if the `qiskit-*.profraw` files are generated in the expected location.

### Scenario 2: Combined Python and Rust Coverage

*   **Hypothesis:** Python coverage (using `coverage.py`) and Rust coverage (using `llvm-cov`) can be collected simultaneously without interference.
*   **Test:**
    1.  Run a Python script that imports Qiskit modules and is instrumented for Python coverage: `coverage run my_python_script.py`.
    2.  After the Python script finishes, run the `llvm-cov` commands to generate Rust coverage reports.
    3.  Verify that both Python coverage data (`.coverage` file) and Rust coverage data (`coverage.lcov`, `coverage.xml`) are generated correctly.

### Scenario 3: Installing New Dependencies

*   **Hypothesis:** Installing new Python dependencies on top of an editable Qiskit installation will not disrupt Rust coverage collection.
*   **Test:**
    1.  Activate the virtual environment.
    2.  Install a new Python package using `pip install <new_package>`.
    3.  Run the Python script that imports Qiskit modules and triggers Rust code execution.
    4.  Run the `llvm-cov` commands to generate Rust coverage reports.
    5.  Verify that the Rust coverage data is still collected correctly after installing the new dependency.
### Scenario 4: Mounting and Running Python Software from a Random Folder

*   **Hypothesis:** Mounting a Python software package into the Docker container from a host directory and running it will allow for the cumulative collection of both Rust and Python coverage data.
*   **Test:**
    1.  Mount the host directory containing the Python software into the container at a random location (e.g., `/app`).
    2.  Activate the virtual environment within the container.
    3.  Run the Python software using `coverage run /app/your_script.py`.
    4.  Generate the Python coverage report using `coverage xml`.
    5.  Run the `llvm-cov` commands to generate Rust coverage reports (`coverage.lcov`, `coverage.xml`).
    6.  Verify that both Python and Rust coverage data are generated and that the reports accurately reflect the coverage from the mounted Python software.