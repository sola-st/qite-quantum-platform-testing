from pathlib import Path
from typing import Any, List, Optional
from qiskit import QuantumCircuit

"""Module to describe a class that takes two circuits and returns a combined circuit.

The class has the following methods:
- combine_circuits: Combine two quantum circuits.

The class is the extended by subclasses that implement the specific combination
strategy.

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
"""


class BaseKnitter:
    def __init__(
            self, circuit1: QuantumCircuit, circuit2: QuantumCircuit) -> None:
        self.circuit1 = circuit1
        self.circuit2 = circuit2

    def _combine_specific(self, circuit: QuantumCircuit,
                          combined_circuit: QuantumCircuit) -> None:
        """Combine a specific circuit into the combined circuit."""
        raise NotImplementedError("Subclasses should implement this method.")
