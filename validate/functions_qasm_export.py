from qiskit import QuantumCircuit
import os
from pathlib import Path
from typing import Optional


def export_to_qasm_with_pytket(
        qiskit_circ: QuantumCircuit, var_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a Qiskit circuit to a Pytket QASM file."""
    from pytket.extensions.qiskit import qiskit_to_tk
    from pytket.qasm import circuit_to_qasm_str

    # Convert Qiskit circuit to Pytket format and save as QASM
    tket_circ = qiskit_to_tk(qiskit_circ.decompose().decompose())
    qasm_str_tket = circuit_to_qasm_str(
        tket_circ, header="qelib1", maxwidth=200)

    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_pytket = current_file.with_name(
            f"{file_stem}_{var_name}_pytket.qasm")
    else:
        file_path_pytket = Path(abs_output_file)

    with open(file_path_pytket, 'w') as f:
        f.write(qasm_str_tket)

    print(f"Saved the Pytket circuit to {file_path_pytket}")
    return file_path_pytket.as_posix()


def export_to_qasm_with_qiskit(
        qiskit_circ: QuantumCircuit, var_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a Qiskit circuit to a Qiskit QASM file."""
    from qiskit import qasm2

    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_qiskit = current_file.with_name(
            f"{file_stem}_{var_name}_qiskit.qasm")
    else:
        file_path_qiskit = Path(abs_output_file)

    # Save Qiskit circuit directly to QASM
    qasm2.dump(qiskit_circ, file_path_qiskit)

    print(f"Saved the Qiskit circuit to {file_path_qiskit}")
    return file_path_qiskit.as_posix()


def export_to_qasm_with_pennylane(
        qiskit_circ: QuantumCircuit, var_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a Qiskit circuit to a PennyLane QASM file."""
    import pennylane as qml
    from pennylane.tape import QuantumTape
    from qiskit import QuantumCircuit
    from pennylane.tape import make_qscript
    from pennylane.tape import QuantumScript

    # Convert Qiskit circuit to a simplified form
    simplified_qiskit_circ = qiskit_circ.decompose().decompose()
    pennylane_quantum_function = qml.from_qiskit(
        simplified_qiskit_circ)
    qs = make_qscript(pennylane_quantum_function)()
    # filter out all the measurements
    new_ops = []
    wires_to_measure = set()
    for op in qs:
        if op.name == 'MidMeasureMP':
            for wire in op.wires.tolist():
                wires_to_measure.add(wire)
        else:
            new_ops.append(op)
    qs_no_meas = QuantumScript(
        new_ops,
        [qml.expval(qml.PauliZ(wire)) for wire in wires_to_measure])

    qasm_str_pennylane = qs_no_meas.to_openqasm(measure_all=True)

    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_pennylane = current_file.with_name(
            f"{file_stem}_{var_name}_pennylane.qasm")
    else:
        file_path_pennylane = Path(abs_output_file)

    # Save PennyLane QASM string to file
    with open(file_path_pennylane, 'w') as f:
        f.write(qasm_str_pennylane)

    print(f"Saved the PennyLane circuit to {file_path_pennylane}")
    return file_path_pennylane.as_posix()


# def export_to_qasm_with_bqskit(
#         qiskit_circ: QuantumCircuit, var_name: str,
#         abs_output_file: str = None) -> Optional[str]:
#     """Export a Qiskit circuit to a BQSKit QASM file."""
#     from bqskit.ext import qiskit_to_bqskit
#     bqskit_circ = qiskit_to_bqskit(qiskit_circ)

#     # Determine file path
#     if not abs_output_file:
#         current_file = Path(__file__)
#         file_stem = current_file.stem
#         file_path_bqskit = current_file.with_name(
#             f"{file_stem}_{var_name}_bqskit.qasm")
#     else:
#         file_path_bqskit = Path(abs_output_file)

#     # Save BQSKit circuit to QASM
#     bqskit_circ.save(str(file_path_bqskit))

#     print(f"Saved the BQSKit circuit to {file_path_bqskit}")
#     return file_path_bqskit.as_posix()


def export_to_qasm_from_proprietary_ir_qiskit(
        circuit: QuantumCircuit, base_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a proprietary IR Qiskit circuit to a QASM file."""
    from qiskit import qasm2
    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_path_qiskit = current_file.with_name(
            f"{base_name}_qiskit.qasm")
    else:
        file_path_qiskit = Path(abs_output_file)
    # Save Qiskit circuit directly to QASM
    qasm2.dump(circuit, file_path_qiskit)
    print(f"Saved the Qiskit circuit to {file_path_qiskit}")
    return file_path_qiskit.as_posix()


def export_to_qasm_from_proprietary_ir_pytket(
        tket_circ, base_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a proprietary IR Pytket circuit to a QASM file."""
    from pytket.qasm import circuit_to_qasm_str
    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_path_pytket = current_file.with_name(
            f"{base_name}_pytket.qasm")
    else:
        file_path_pytket = Path(abs_output_file)
    # Save Pytket circuit to QASM
    qasm_str_tket = circuit_to_qasm_str(
        tket_circ, header="qelib1", maxwidth=200)
    file_path_pytket.write_text(qasm_str_tket)
    print(f"Saved the Pytket circuit to {file_path_pytket}")
    return file_path_pytket.as_posix()


def export_to_qasm_from_proprietary_ir_pennylane(
        pennylane_quantum_function, base_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a proprietary IR PennyLane circuit to a QASM file."""
    import pennylane as qml
    from pennylane.tape import make_qscript
    from pennylane.tape import QuantumScript
    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_path_pennylane = current_file.with_name(
            f"{base_name}_pennylane.qasm")
    else:
        file_path_pennylane = Path(abs_output_file)
    # Save PennyLane circuit to QASM
    qs = make_qscript(pennylane_quantum_function)()
    # filter out all the measurements
    new_ops = []
    wires_to_measure = set()
    for op in qs:
        if op.name == 'MidMeasureMP':
            for wire in op.wires.tolist():
                wires_to_measure.add(wire)
        else:
            new_ops.append(op)
    qs_no_meas = QuantumScript(
        new_ops,
        [qml.expval(qml.PauliZ(wire)) for wire in wires_to_measure])

    qasm_str_pennylane = qs_no_meas.to_openqasm(measure_all=True)
    file_path_pennylane.write_text(qasm_str_pennylane)
    print(f"Saved the PennyLane circuit to {file_path_pennylane}")
    return file_path_pennylane.as_posix()


# def export_to_qasm_from_proprietary_ir_bqskit(
#         bqskit_circ, base_name: str,
#         abs_output_file: str = None) -> Optional[str]:
#     """Export a proprietary IR BQSKit circuit to a QASM file."""
#     # Determine file path
#     if not abs_output_file:
#         current_file = Path(__file__)
#         file_path_bqskit = current_file.with_name(
#             f"{base_name}_bqskit.qasm")
#     else:
#         file_path_bqskit = Path(abs_output_file)
#     # Save BQSKit circuit to QASM
#     bqskit_circ.save(str(file_path_bqskit))
#     print(f"Saved the BQSKit circuit to {file_path_bqskit}")
#     return file_path_bqskit.as_posix()
