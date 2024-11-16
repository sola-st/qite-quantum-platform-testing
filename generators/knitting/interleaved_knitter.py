from qiskit import QuantumCircuit
from typing import List, Callable, Optional, Union, Dict, Tuple
from generators.knitting.base_knitter import BaseKnitter
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit.library import Barrier
from uuid import uuid4
from typing import Any

"""Module with a generator strategy that schedules instructions from two quantum circuits alternately.

Interleaved execution means that instructions from the two circuits are scheduled alternately,
executing one instruction from the first circuit followed by one from the second circuit.
The resulting circuit will have a size equal to the sum of the sizes of the input circuits.

- interleaved_combine_circuits: Schedule instructions from two quantum circuits alternately.

When the circuits act on different registers of given size:
- Circuit 1: (q0, 5), (c0, 5), (c1, 3)
- Circuit 2: (q0, 2), (q1, 3), (c0, 2), (c1, 7)

We sort the registers of both circuits by size (keeping a distinction between qubits and classical bits):
- Circuit 1: (q0, 5), (c0, 5), (c1, 3)
- Circuit 2: (q1, 3), (q0, 2), (c1, 7), (c0, 2)

Then we create a mapping, where each register is either mapped to itself or to a new register with a unique name (belonging to the other circuit):
- Circuit 1:
    (q0, 5) -> remains the same,
    (c0, 5) -> (c1_circuit2, 7),
    (c1, 3) -> remains the same
- Circuit 2:
    (q1, 3) -> (q0_circuit1, 5),
    (q0, 2) -> remains the same,
    (c1, 7) -> remains the same,
    (c0, 2) -> (c1_circuit1, 3)

Focusing on one type of register at a time
    The algorithm adds a flag to track each register's orgin
    Then it sorts the registers by size
    Then it iterates over the registers and for each contiguous registers
    of different origin, it creates a mapping between them (where the smallest
    is mapped to the largest, and the largest is mapped to itself)
    Then the remaining registers are mapped to themselves.

"""

from qiskit.converters import (
    circuit_to_dag,
    dag_to_circuit
)
from qiskit import (
    QuantumRegister,
    ClassicalRegister,
)
from qiskit.circuit import (
    Qubit,
    Clbit,
)


class InterleavedKnitter(BaseKnitter):

    def _get_register_mapping(
        self,
        registers_circ1: List[Union[QuantumRegister, ClassicalRegister]],
        registers_circ2: List[Union[QuantumRegister, ClassicalRegister]],
    ):
        """Create a mapping between registers of the two circuits."""
        # Combine and sort registers by size, keeping qubits and classical bits separate
        all_registers_w_provenance = []
        all_registers_w_provenance.extend(
            [(reg, 1) for reg in registers_circ1])
        all_registers_w_provenance.extend(
            [(reg, 2) for reg in registers_circ2])
        quantum_registers = [
            (reg, provenance)
            for reg, provenance in all_registers_w_provenance
            if isinstance(reg, QuantumRegister)]
        classical_registers = [
            (reg, provenance)
            for reg, provenance in all_registers_w_provenance
            if isinstance(reg, ClassicalRegister)]
        sorted_quantum_registers = sorted(
            quantum_registers, key=lambda reg: reg[0].size, reverse=True)
        sorted_classical_registers = sorted(
            classical_registers, key=lambda reg: reg[0].size, reverse=True)
        print("sorted_quantum_registers: ", sorted_quantum_registers)
        print("sorted_classical_registers: ", sorted_classical_registers)

        mapping: Dict[str, Any] = {}

        i = 0
        while i < len(sorted_quantum_registers):
            # map the last register to itself
            if i == len(sorted_quantum_registers) - 1:
                i_reg, i_provenance = sorted_quantum_registers[i]
                mapping[i_reg.name] = i_reg
                break
            i_reg, i_provenance = sorted_quantum_registers[i]
            next_i_reg, next_i_provenance = sorted_quantum_registers[i + 1]
            # map the largest to itself
            mapping[i_reg.name] = i_reg
            # if of different provenance,
            if i_provenance != next_i_provenance:
                # map the smallest to the largest
                # the largest is always first in the list by construction
                mapping[next_i_reg.name] = i_reg
                i += 2
            else:
                i += 1

        i = 0
        while i < len(sorted_classical_registers):
            # map the last register to itself
            if i == len(sorted_classical_registers) - 1:
                i_reg, i_provenance = sorted_classical_registers[i]
                mapping[i_reg.name] = i_reg
                break
            i_reg, i_provenance = sorted_classical_registers[i]
            next_i_reg, next_i_provenance = sorted_classical_registers[i + 1]
            # map the largest to itself
            mapping[i_reg.name] = i_reg
            # if of different provenance,
            if i_provenance != next_i_provenance:
                # map the smallest to the largest
                # the largest is always first in the list by construction
                mapping[next_i_reg.name] = i_reg
                i += 2
            else:
                i += 1

        return mapping

    def combine_circuits(self) -> QuantumCircuit:
        """Combine two quantum circuits by interleaving their instructions.

        This method takes two quantum circuits and combines them into a single
        quantum circuit by interleaving their instructions. The resulting circuit
        will have all the quantum and classical registers from both circuits, with
        unique names to avoid conflicts.

        Returns:
            QuantumCircuit: A new quantum circuit that interleaves the operations
            of self.circuit1 and self.circuit2.
        """
        dag_circuit1 = circuit_to_dag(self.circuit1)
        dag_circuit2 = circuit_to_dag(self.circuit2)
        new_dag = DAGCircuit()
        prefix_circuit1 = str(uuid4())[:6]
        prefix_circuit2 = str(uuid4())[:6]
        registers_circ1 = self._rename_registers(
            prefix_circuit1, self.circuit1.qregs + self.circuit1.cregs)
        registers_circ2 = self._rename_registers(
            prefix_circuit2, self.circuit2.qregs + self.circuit2.cregs)
        reference_to_registers = self._get_register_mapping(
            registers_circ1, registers_circ2)
        # add the new registers to the new DAG
        unique_new_registers = set(reference_to_registers.values())
        for new_reg in unique_new_registers:
            new_dag.add_qreg(new_reg) if isinstance(
                new_reg, QuantumRegister) else new_dag.add_creg(new_reg)

        nodes_circuit1 = list(dag_circuit1.topological_op_nodes())
        nodes_circuit2 = list(dag_circuit2.topological_op_nodes())
        max_length = max(len(nodes_circuit1), len(nodes_circuit2))

        for i in range(max_length):
            if i < len(nodes_circuit1):
                self._apply_operation(
                    nodes_circuit1[i],
                    prefix_circuit1, reference_to_registers, new_dag)
            if i < len(nodes_circuit2):
                self._apply_operation(
                    nodes_circuit2[i],
                    prefix_circuit2, reference_to_registers, new_dag)

        combined_qc = dag_to_circuit(new_dag)
        return combined_qc
