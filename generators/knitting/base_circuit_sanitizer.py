from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from qiskit import QuantumCircuit
import qiskit.circuit.library as gate_library_module
import inspect

"""Module that transforms circuits.

There is a base class CicuitSaniizer that defines the interface for the
transformations. The transformations are implemented in subclasses, using the
method `sanitize`.

# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- avoid function with a single line which is a function call
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib every time that paths are checked, created or composed.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate
- make sure that any output folder exists before storing file in it, otherwise create it.
"""

console = Console()


class CircuitSanitizer:

    def __init__(self, sanitization_level: int = 1):
        """Initialize the RemoveMeasurementSanitizer."""
        self.sanitization_level = sanitization_level

    def sanitize(self, circuit: QuantumCircuit) -> QuantumCircuit:
        raise NotImplementedError("Subclasses should implement this method")

    def prepare_circuit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Decompose the circuit to the specified level."""
        for _ in range(self.sanitization_level):
            circuit = circuit.decompose()
        return circuit
