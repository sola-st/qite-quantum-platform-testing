"""Module implements the CircuitSanitizer for sanitizing quantum circuits.

The sanitizers handle cases where the circuit has:
- unbound parameters
- measurements
- mid-circuit measurements
- resets
- conditional operations
- classical registers
- custom gates
- etc.

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

from typing import Any
from rich.console import Console

from .base_circuit_sanitizer import CircuitSanitizer
from qiskit import QuantumCircuit
from qiskit.converters import (
    circuit_to_dag,
    dag_to_circuit
)


class RemoveMeasurementsSanitizer(CircuitSanitizer):

    def sanitize(self, circuit: Any) -> Any:
        """Remove measurements from the circuit."""
        circuit = self.prepare_circuit(circuit)
        new_circuit = self._remove_measurements(circuit)
        return new_circuit

    def _remove_measurements(self, circuit: Any) -> QuantumCircuit:
        """Helper function to remove measurements."""
        new_circuit_data = []
        for instruction in circuit.data:
            if instruction.operation.name != 'measure':
                new_circuit_data.append(instruction)
        new_circuit = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)
        for instruction in new_circuit_data:
            new_circuit.append(
                instruction, circuit.qubits, circuit.clbits)
        return new_circuit


class RemoveMidCircuitMeasurementsSanitizer(CircuitSanitizer):

    def sanitize(self, circuit: Any) -> Any:
        """Remove mid-circuit measurements from the circuit."""
        circuit = self.prepare_circuit(circuit)
        new_circuit = self._remove_mid_circuit_measurements(circuit)
        return new_circuit

    def _remove_mid_circuit_measurements(self, circuit: Any) -> QuantumCircuit:
        """Helper function to remove mid-circuit measurements.

        Note that it keeps any measurements at the end of the circuit.
        It traverses the circuit from the end and whenever it finds the first
        non-measurement operation it flags that qubit line as dirty and
        every successive measurement on that line is removed.
        """
        dag = circuit_to_dag(circuit)
        dirty_qubits = set()
        for node in list(dag.topological_op_nodes())[::-1]:
            print(node.name)
            if node.name != 'measure':
                dirty_qubits.update(node.qargs)
            elif any(qubit in dirty_qubits for qubit in node.qargs):
                dag.remove_op_node(node)
        return dag_to_circuit(dag)
