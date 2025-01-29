# Dataset for Fine-Tuning

Goal: create a dataset of programs before and after the major release of Qiskit (0.45.0 -> 1.2.0).

1. To scrape the release sheets:

```bash
python -m information_distillation.get_changelogs --repo_url https://github.com/Qiskit/qiskit --release_notes_dir releasenotes/notes/ --output_dir data/changelogs/v001/changes --repo_dir data/changelogs/v001/repo
```
The output is in the `data/changelogs/v001/changes/snapshot_changes` directory.

2. Build docker image to run program of OLD version:

```bash
cd docker/qiskit_custom_version
docker build --build-arg QISKIT_VERSION=0.45.0 --build-arg GID=$(id -g) --build-arg UID=$(id -u) -t qiskit_image_0.45.0 .
# test it with:
docker run --rm qiskit_image_0.45.0
# mount and run the program
cd ../..
docker run --rm -it -v $(pwd)/data/finetuning/datasets/seeds:/workspace/ qiskit_image_0.45.0 python /workspace/old_sample.py
```

3. Build docker image to run program of NEW version:

```bash
cd docker/qiskit_custom_version
docker build --build-arg QISKIT_VERSION=1.2.0 --build-arg GID=$(id -g) --build-arg UID=$(id -u) -t qiskit_image_1.2.0 .
# test it with:
docker run --rm qiskit_image_1.2.0
# mount and run the program
cd ../..
docker run --rm -it -v $(pwd)/data/finetuning/datasets/seeds:/workspace/ qiskit_image_1.2.0 python /workspace/new_sample.py
```


## Bootstrap some examples

1. Ask LLM to brainstorm exercises:
```
Provide 20 innovative and actionable strategies or ideas to address the following topic: possible programming exercise for a starter qiskit programmer
###
Here are 20 innovative and actionable strategies or ideas for a starter Qiskit programmer to practice and improve their skills:

Quantum Circuit Simulator: Create a simple quantum circuit simulator using Qiskit that can simulate the behavior of quantum bits (qubits) and gates.
Quantum Teleportation: Implement a quantum teleportation protocol using Qiskit, which allows for the transfer of quantum information from one qubit to another without physical transport of the qubits.
Superdense Coding: Implement a superdense coding protocol using Qiskit, which allows for the transmission of multiple classical bits of information through a single qubit.
Quantum Random Number Generator: Create a quantum random number generator using Qiskit that can generate truly random numbers based on the principles of quantum mechanics.
Deutsch-Jozsa Algorithm: Implement the Deutsch-Jozsa algorithm using Qiskit, which is a quantum algorithm that can solve a specific problem exponentially faster than any known classical algorithm.
Bernstein-Vazirani Algorithm: Implement the Bernstein-Vazirani algorithm using Qiskit, which is a quantum algorithm that can solve a specific problem quadratically faster than any known classical algorithm.
Quantum Fourier Transform: Implement a quantum Fourier transform using Qiskit, which is a quantum algorithm that can efficiently calculate the discrete Fourier transform of a quantum state.
Shor's Algorithm: Implement Shor's algorithm using Qiskit, which is a quantum algorithm that can factor large numbers exponentially faster than any known classical algorithm.
Grover's Algorithm: Implement Grover's algorithm using Qiskit, which is a quantum algorithm that can search an unsorted database quadratically faster than any known classical algorithm.
Quantum Error Correction: Implement a simple quantum error correction code using Qiskit, such as a 3-qubit bit-flip code or a 5-qubit phase-flip code.
Quantum Cryptography: Implement a simple quantum cryptography protocol using Qiskit, such as a quantum key distribution (QKD) protocol.
Quantum Circuit Optimization: Use Qiskit to optimize a quantum circuit by reducing the number of gates or qubits required to implement a specific quantum algorithm.
Quantum Simulation of a Physical System: Use Qiskit to simulate the behavior of a simple physical system, such as a harmonic oscillator or a spin chain.
Quantum Machine Learning: Implement a simple quantum machine learning algorithm using Qiskit, such as a quantum support vector machine (SVM) or a quantum k-means clustering algorithm.
Quantum Circuit Synthesis: Use Qiskit to synthesize a quantum circuit from a high-level description of a quantum algorithm or protocol.
Quantum Circuit Visualization: Use Qiskit to visualize a quantum circuit and its properties, such as the circuit's topology or the qubits' entanglement.
Quantum Algorithm Benchmarking: Use Qiskit to benchmark the performance of a quantum algorithm or protocol on a real quantum device or simulator.
Quantum Software Development: Use Qiskit to develop a quantum software application, such as a quantum game or a quantum simulator.
Quantum Protocols and Games: Implement a simple quantum protocol or game using Qiskit, such as a quantum version of the famous "Prisoner's Dilemma" game.
Quantum Tunneling: Simulate quantum tunneling using Qiskit, which is a quantum phenomenon where a particle can pass through a potential energy barrier even if it doesn't have enough energy to classically overcome the barrier.
```


1. First generation: with groq LLama 3.3 70B,
2. then use copilot chat to fix the code with `fix \n <full error stack track - std out>`.


### Use NotebookLM to upgrade

Context:
- concat release notes 1.0, 1.1, 1.2
- packaging changes: https://docs.quantum.ibm.com/migration-guides/qiskit-1.0-installation
- feature changes: https://docs.quantum.ibm.com/migration-guides/qiskit-1.0-features
```
<program v0.45>
upgrade to v1 qiskit
```