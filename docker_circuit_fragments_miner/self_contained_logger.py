"""This module contains a self-contained logger function.

The function scans all the objects accessible in the current scope and logs all
the objects that are instances of the QuantumCircuit class.
Each quantum circuit is stored as pickled file in the STORAGE_PATH.
The name of each file is the hash of the quantum circuit object.

# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- avoid function with a single line which is a function call
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib every time that paths are checked, created or composed.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate
- make sure that any output folder exists before storing file in it, otherwise create it.

"""
from pathlib import Path
from typing import Any, List, Optional, Type
try:
    from qiskit import QuantumCircuit
except ImportError:
    # skip if this log is added to configuration python files before qiskit is installed
    pass
import pickle

STORAGE_PATH = Path(
    '/opt/circuit_storage')


def log_quantum_circuits(scope: Optional[dict] = None) -> None:
    """Logs all QuantumCircuit instances in the provided scope."""
    try:
        from qiskit import QuantumCircuit
    except ImportError:
        # skip if this log is added to configuration python files before qiskit is installed
        return

    scope = {**globals(), **(scope or {})}
    quantum_circuits = find_instances(scope=scope, cls=QuantumCircuit)
    ensure_storage_path_exists()
    log_circuits(quantum_circuits=quantum_circuits)


def find_instances(scope: dict, cls: Type) -> List[Any]:
    """Finds all instances of a specific class within a given scope."""
    return [obj for obj in scope.values() if isinstance(obj, cls)]


def ensure_storage_path_exists() -> None:
    """Ensures that the storage path exists."""
    if not STORAGE_PATH.exists():
        STORAGE_PATH.mkdir(parents=True, exist_ok=True)


def log_circuits(quantum_circuits: List[Any]) -> None:
    """Logs each QuantumCircuit instance."""
    for circuit in quantum_circuits:
        log_circuit(circuit=circuit)


def log_circuit(circuit: Any) -> None:
    """Logs a single QuantumCircuit instance."""
    circuit_hash = hash(circuit.draw())
    file_path = STORAGE_PATH / f"{circuit_hash}.pkl"
    with file_path.open('wb') as file:
        pickle.dump(circuit, file)
