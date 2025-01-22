
from qiskit import QuantumCircuit
import os
from pathlib import Path
from typing import Optional, Tuple, Any


def convert_to_pennylane(
        qiskit_circ: QuantumCircuit, var_name: str) -> Tuple[str, Any]:
    """Export a Qiskit circuit to a PennyLane Quantum Function."""
    import pennylane as qml
    from pennylane.tape import make_qscript
    my_qfunc = qml.from_qiskit(qiskit_circ)
    return my_qfunc, var_name
    # qs = make_qscript(my_qfunc)()
    # return qs, var_name
