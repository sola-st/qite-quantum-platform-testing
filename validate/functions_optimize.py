import os
from copy import deepcopy
from pathlib import Path
from typing import Optional

from qiskit import QuantumCircuit
from pytket import Circuit as tkCircuit
from bqskit import Circuit as bqCircuit
import pennylane as qml


def optimize_with_pytket(
        tkqc, var_name: str, output_dir: Optional[str] = None):
    """Optimize a pytket circuit and export as qasm."""
    from pytket.qasm import circuit_to_qasm_str
    from pytket.passes import (
        FullPeepholeOptimise, PeepholeOptimise2Q, RemoveRedundancies,
        EulerAngleReduction, KAKDecomposition,
        CliffordPushThroughMeasures, FlattenRegisters,
        PauliSimp, GreedyPauliSimp,
        OptimisePhaseGadgets,
        ZXGraphlikeOptimisation
    )
    from pytket.circuit import OpType

    optimization_passes = {
        "FullPeepholeOptimise": FullPeepholeOptimise(),
        "PeepholeOptimise2Q": PeepholeOptimise2Q(),
        "RemoveRedundancies": RemoveRedundancies(),
        "EulerAngleReduction": EulerAngleReduction(q=OpType.Rz, p=OpType.Rx),
        "KAKDecomposition": KAKDecomposition(),
        "CliffordPushThroughMeasures": CliffordPushThroughMeasures(),
        "FlattenRegisters": FlattenRegisters(),
        "PauliSimp": PauliSimp(),
        "GreedyPauliSimp": GreedyPauliSimp(),
        "OptimisePhaseGadgets": OptimisePhaseGadgets(),
        "ZXGraphlikeOptimisation": ZXGraphlikeOptimisation()
    }

    for opt_pass_name, optimization_pass in optimization_passes.items():
        i_qc = deepcopy(tkqc)
        optimization_pass.apply(i_qc)
        i_opt_circuit_qasm = circuit_to_qasm_str(
            i_qc, header="qelib1", maxwidth=200)

        # Determine file path
        if output_dir is not None:
            file_path_pytket = Path(
                output_dir) / f"{var_name}_{opt_pass_name}_pytket.qasm"
        else:
            current_file = Path(__file__)
            file_stem = current_file.stem
            file_path_pytket = current_file.with_name(
                f"{file_stem}_{var_name}_{opt_pass_name}_pytket.qasm")

        with open(file_path_pytket, 'w') as f:
            f.write(i_opt_circuit_qasm)

        print(
            f"Saved Optimized Pytket circuit ({opt_pass_name}) to {file_path_pytket}")


def optimize_with_qiskit(
        qiskit_circ: QuantumCircuit, var_name: str,
        output_dir: Optional[str] = None):
    """Optimize a Qiskit circuit and export as qasm."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit.qasm2 import dump

    for optimization_level in range(4):
        pass_manager = generate_preset_pass_manager(
            optimization_level=optimization_level,
            seed_transpiler=12345)
        i_qc = deepcopy(qiskit_circ)
        i_qc = pass_manager.run(i_qc)

        # Determine file path
        if output_dir is not None:
            file_path_qiskit = Path(
                output_dir) / f"{var_name}_opt_level_{optimization_level}_qiskit.qasm"
        else:
            current_file = Path(__file__)
            file_stem = current_file.stem
            file_path_qiskit = current_file.with_name(
                f"{file_stem}_{var_name}_opt_level_{optimization_level}_qiskit.qasm")

        # Save Qiskit circuit directly to QASM
        dump(i_qc, file_path_qiskit)

        print(
            f"Saved Optimized Qiskit circuit (optimization level {optimization_level}) to {file_path_qiskit}")


def optimize_with_pennylane(
        pnqc, var_name: str,
        output_dir: Optional[str] = None):
    """Optimize a PennyLane circuit and export as qasm."""
    import pennylane as qml
    from pennylane.tape import QuantumTape
    from copy import deepcopy

    # print("Un-optimized PennyLane circuit:")
    # print(qml.draw(pnqc)())

    # print("Optimized PennyLane circuit:")
    optimized_circuit = deepcopy(pnqc)
    optimized_circuit = qml.compile(optimized_circuit)
    # optimized_circuit = qml.transforms.cancel_inverses(optimized_circuit)
    # optimized_circuit = qml.transforms.merge_rotations(optimized_circuit)
    # optimized_circuit = qml.transforms.single_qubit_fusion(optimized_circuit)
    # print(qml.draw(optimized_circuit)())
    # Define measurement and PennyLane device
    # measurements = [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    # circuit_fn = qml.from_qiskit(
    #     simplified_qiskit_circ, measurements=measurements)

    # add one measurement to the circuit
    dev = qml.device('default.qubit', wires=128)

    @qml.qnode(dev)
    def optimized_circuit_qnode():
        optimized_circuit()
        return qml.expval(qml.PauliZ(0))

    # Extract the QASM from the PennyLane QNode
    with QuantumTape(shots=10) as tape:
        optimized_circuit_qnode.construct([], {})
        qasm_str_pennylane = optimized_circuit_qnode.tape.to_openqasm(
            wires=sorted(
                tape.wires))

    # Determine file path
    if output_dir is not None:
        file_path_pennylane = Path(
            output_dir) / f"{var_name}_optimized_pennylane.qasm"
    else:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_pennylane = current_file.with_name(
            f"{file_stem}_{var_name}_optimized_pennylane.qasm")

    # Save PennyLane QASM string to file
    with open(file_path_pennylane, 'w') as f:
        f.write(qasm_str_pennylane)

    print(f"Saved the PennyLane circuit to {file_path_pennylane}")


# def optimize_with_bqskit(
#         bqqc, var_name: str,
#         output_dir: Optional[str] = None):
#     """Optimize a BQSKit circuit and export as qasm."""
#     from bqskit.passes import (
#         QuickPartitioner, ScanningGateRemovalPass, UnfoldPass,
#     )
#     from bqskit.compiler import (
#         Workflow, Compiler
#     )
#     from bqskit import compile
#     # from bqskit.passes import (
#     #     QuickPartitioner, ForEachBlockPass,
#     #     ScanningGateRemovalPass, UnfoldPass,
#     #     ExhaustiveGateRemovalPass,
#     #     IterativeScanningGateRemovalPass,
#     #     TreeScanningGateRemovalPass
#     # )

#     # workflows = [
#     #     Workflow([
#     #         QuickPartitioner(3),  # Partition into 3-qubit blocks
#     #         # Apply gate deletion to each block (in parallel)
#     #         ForEachBlockPass(ScanningGateRemovalPass()),
#     #         UnfoldPass(),  # Unfold the blocks back into the original circuit
#     #     ]),
#     # ]
#     opt_bqqc = compile(bqqc, max_synthesis_size=5)
#     # with Compiler() as compiler:
#     # example of using specific workflow
#     # opt_bqqc = compiler.compile(bqqc, workflow=workflows[0])

#     # Determine file path
#     if output_dir is not None:
#         file_path_bqskit = Path(
#             output_dir) / f"{var_name}_optimized_bqskit.qasm"
#     else:
#         current_file = Path(__file__)
#         file_stem = current_file.stem
#         file_path_bqskit = current_file.with_name(
#             f"{file_stem}_{var_name}_optimized_bqskit.qasm")

#     # Save BQSKit circuit to QASM
#     opt_bqqc.save(str(file_path_bqskit))

#     print(
#         f"Saved Optimized BQSKit circuit to {file_path_bqskit}")
