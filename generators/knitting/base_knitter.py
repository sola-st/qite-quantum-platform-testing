from pathlib import Path
from typing import Any, List, Optional, Dict, Tuple, Union
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.dagcircuit import DAGCircuit
from qiskit import QuantumRegister, ClassicalRegister
from qiskit.circuit import Qubit, Clbit
from uuid import uuid4


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

    def _replace_register_names(
        self,
        reference_list: Tuple[
            Union[Qubit, Clbit, QuantumRegister, ClassicalRegister]],
        register_bank: Dict[str, Union[QuantumRegister, ClassicalRegister]],
        prefix: str,
        qubit_shift: int = 0,
        clbit_shift: int = 0,
    ) -> Tuple[Union[Qubit, Clbit, QuantumRegister, ClassicalRegister]]:
        """Replace the register or bit references with new ones.

        The new name is the old name with a prefix, joined with an underscore.
        The register bank is a dictionary that maps the new register names to
        the new objects.
        """
        # print("Reference list: ", reference_list)
        new_references = []
        for reference in reference_list:
            if isinstance(reference, (QuantumRegister, ClassicalRegister)):
                new_name = f"{prefix}_{reference.name}"
                new_register = register_bank[new_name]
                new_references.append(new_register)
            elif isinstance(reference, (Qubit, Clbit)):
                new_name = f"{prefix}_{reference._register.name}"
                new_register = register_bank[new_name]
                new_references.append(
                    new_register[reference._index + clbit_shift])
        return tuple(new_references)

    def _create_reference_to_registers(
            self,
            qregs: List[QuantumRegister],
            cregs: List[ClassicalRegister],
            prefix: str,
            new_dag: DAGCircuit
    ) -> Dict[str, Union[QuantumRegister, ClassicalRegister]]:
        reference_to_registers = {}
        for qreg in qregs:
            new_name = f"{prefix}_{qreg.name}"
            new_qreg = QuantumRegister(qreg.size, new_name)
            new_dag.add_qreg(new_qreg)
            reference_to_registers[new_name] = new_qreg
        for creg in cregs:
            new_name = f"{prefix}_{creg.name}"
            new_creg = ClassicalRegister(creg.size, new_name)
            new_dag.add_creg(new_creg)
            reference_to_registers[new_name] = new_creg
        return reference_to_registers
