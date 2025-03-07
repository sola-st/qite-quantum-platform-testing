FROM ubuntu:24.04


RUN apt-get update && apt-get upgrade -y
RUN apt-get update && \
        apt-get install -y python3 python3-pip python3-venv python3-dev \
        python3-setuptools \
        python3-wheel \
        python3-coverage \
        python3-launchpadlib \
        git \
        build-essential \
        curl \
        lcov \
        llvm \
        wget \
        libssl-dev \
        libgmp-dev \
        libmpfr-dev \
        libmpc-dev \
        software-properties-common

# install CMAKE v 3.26 - Pytket
RUN mkdir -p /tmp/cmake && \
    cd /tmp/cmake && \
    wget https://cmake.org/files/v3.26/cmake-3.26.1.tar.gz && \
    tar -xzvf cmake-3.26.1.tar.gz
ENV OPENSSL_ROOT_DIR=/usr/lib/ssl
RUN cd /tmp/cmake/cmake-3.26.1/ && \
    ./bootstrap && \
    make -j$(nproc) && \
    make install && \
    cd / && \
    rm -rf /tmp/cmake

ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID regularuser && \
    useradd -m -u $UID -g $GID -s /bin/bash regularuser

# Set environment variable to avoid issues with pip and locales
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Install Python packages needed for building and testing
USER regularuser
WORKDIR /home/regularuser
RUN python3 -m venv .venv
RUN . .venv/bin/activate && pip install --no-cache-dir \
    coverage==7.6.2 \
    cython \
    unidiff \
    click \
    rich \
    pytest \
    pytest-cov \
    stestr \
    ddt \
    lcov_cobertura==1.6 \
    pytest \
    pytest-cov \
    conan


# Install RUST - for Qiskit

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/regularuser/.cargo/bin:${PATH}"
RUN rustup component add llvm-tools-preview
RUN cargo install cargo-llvm-cov grcov rustfilt

# Build and install qiskit-terra with coverage instrumentation
ENV CARGO_INCREMENTAL=0 \
    RUSTFLAGS="-Cinstrument-coverage" \
    LLVM_PROFILE_FILE="qiskit-%p-%m.profraw" \
    PYTHON="coverage run --source qiskit --parallel-mode" \
    QISKIT_TEST_CAPTURE_STREAMS=1 \
    QISKIT_PARALLEL=FALSE \
    RUST_DEBUG=1


# Install Qiskit version 1.2.4
WORKDIR /home/regularuser
RUN git clone https://github.com/Qiskit/qiskit.git && \
    cd /home/regularuser/qiskit && \
    git checkout tags/1.2.4
RUN . /home/regularuser/.venv/bin/activate && \
    cd /home/regularuser/qiskit && \
    pip install maturin setuptools-rust && if [ -f constraints.txt ]; then \
        pip install --no-cache-dir -c constraints.txt --upgrade pip setuptools wheel && \
        pip install --no-cache-dir -c constraints.txt -e . ; \
    else \
        pip install --no-cache-dir --upgrade pip setuptools wheel && \
        pip install --no-cache-dir -e . ; \
    fi && \
    rm qiskit-*.profraw


# Install Pytket version 1.33.1


WORKDIR /home/regularuser
RUN git clone https://github.com/CQCL/tket.git && \
    cd /home/regularuser/tket && \
    git checkout tags/v1.33.1

# prepare settings for conan (package manager for CPP files)
RUN . /home/regularuser/.venv/bin/activate && \
    cd /home/regularuser/tket && \
    conan profile detect && \
    DEFAULT_PROFILE_PATH=$(conan profile path default) && \
    PROFILE_PATH=./conan-profiles/ubuntu-24.04 && \
    diff ${DEFAULT_PROFILE_PATH} ${PROFILE_PATH} || true && \
    cp ${PROFILE_PATH} ${DEFAULT_PROFILE_PATH} && \
    conan remote add tket-libs https://quantinuumsw.jfrog.io/artifactory/api/conan/tket1-libs --index 0

WORKDIR /home/regularuser/tket
# build the TKET package (CPP) with coverage
# (see option: -s build_type=Debug -o "tket/*":profile_coverage=True)
RUN . /home/regularuser/.venv/bin/activate && \
    conan create tket \
        --version 1.3.32 --user=tket --channel=stable \
        --build="tket*" \
        -o "boost/*":header_only=True \
        -o "tklog/*":shared=True \
        -o "tket/*":shared=True \
        -tf "" \
        -s build_type=Debug \
        -o "tket/*":profile_coverage=True && \
    conan remove -c "pybind11/*" && \
    conan create recipes/pybind11 \
        -s build_type=Debug -o "tket/*":profile_coverage=True && \
    conan create recipes/pybind11_json/all --version=0.2.14 \
         -s build_type=Debug -o "tket/*":profile_coverage=True

# change setup.py to include coverage (when installing python bindings)
RUN sed -i 's/"--build=missing",/"--build=missing", "-o", '\''tket\/\*:profile_coverage=True'\'', "-s", "build_type=Debug",/' pytket/setup.py

# install pytket (python bindings of TKET)
WORKDIR /home/regularuser/tket/pytket
RUN . /home/regularuser/.venv/bin/activate && \
    python -m pip install . -v  && \
    pip install -r tests/requirements.txt


# prepare folder for QITE app
RUN mkdir -p /home/regularuser/app && \
    mkdir -p /home/regularuser/databank && \
    mkdir -p /home/regularuser/databank/tests/e2e/config && \
    chown -R regularuser:regularuser /home/regularuser/app && \
    chown -R regularuser:regularuser /home/regularuser/tket && \
    chown -R regularuser:regularuser /home/regularuser/qiskit && \
    chown -R regularuser:regularuser /home/regularuser/databank && \
    chown -R regularuser:regularuser /home/regularuser/databank/tests/e2e/config


# make sure that each command is run in the virtual environment
RUN echo "source /home/regularuser/.venv/bin/activate" >> /home/regularuser/.bashrc

USER root
RUN apt-get update && apt-get install -y gcovr llvm-16 screen
RUN echo 'root:Docker!' | chpasswd
# RUN ln -fs /usr/share/zoneinfo/CET /etc/localtime && dpkg-reconfigure -f noninteractive tzdata
USER regularuser

CMD ["/bin/bash"]