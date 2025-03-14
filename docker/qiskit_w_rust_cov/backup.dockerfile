# Use the slim Python 3.10 image
FROM python:3.10-slim

ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID regularuser && \
    useradd -m -u $UID -g $GID -s /bin/bash regularuser

# Set environment variable to avoid issues with pip and locales
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Install Python packages needed for building and testing
RUN pip install --no-cache-dir \
    coverage==7.6.2 \
    cython \
    unidiff \
    click \
    rich \
    pytest \
    pytest-cov \
    stestr \
    ddt \
    lcov_cobertura==1.6

# Switch to the regularuser
# install rust
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    lcov \
    llvm
    # \ && apt-get clean && rm -rf /var/lib/apt/lists/*

USER regularuser


RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/regularuser/.cargo/bin:${PATH}"

RUN rustup component add llvm-tools-preview
RUN cargo install cargo-llvm-cov grcov


# Build and install qiskit-terra with coverage instrumentation
ENV CARGO_INCREMENTAL=0 \
    RUSTFLAGS="-Cinstrument-coverage" \
    LLVM_PROFILE_FILE="qiskit-%p-%m.profraw" \
    PYTHON="coverage run --source qiskit --parallel-mode" \
    QISKIT_TEST_CAPTURE_STREAMS=1 \
    QISKIT_PARALLEL=FALSE


RUN pip install coverage pytest pytest-cov

# Install Qiskit version 1.2.0
ENV RUST_DEBUG=1


WORKDIR /home/regularuser
RUN git clone https://github.com/Qiskit/qiskit.git
WORKDIR /home/regularuser/qiskit
RUN git checkout tags/1.2.4
RUN python -m venv .venv
RUN . .venv/bin/activate && pip install maturin coverage setuptools-rust && if [ -f constraints.txt ]; then \
        pip install --no-cache-dir -c constraints.txt --upgrade pip setuptools wheel && \
        pip install --no-cache-dir -c constraints.txt -e . ; \
    else \
        pip install --no-cache-dir --upgrade pip setuptools wheel && \
        pip install --no-cache-dir -e . ; \
    fi

# RUN source <(cargo llvm-cov show-env --export-prefix)
# RUN export CARGO_TARGET_DIR=$CARGO_LLVM_COV_TARGET_DIR
# RUN export CARGO_INCREMENTAL=1
# RUN grcov . --binary-path target/debug/ --source-dir . --output-type lcov --output-path rust.info --llvm --branch --parallel --keep-only 'crates/*'

RUN rustup component add llvm-tools-preview



COPY . /home/regularuser/qiskit



# Set the default command to run the Python script
CMD ["python", "base_qc_w_opt.py"]