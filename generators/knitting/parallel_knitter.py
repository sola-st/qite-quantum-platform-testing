from qiskit import QuantumCircuit
from typing import List, Callable, Optional, Union, Dict, Tuple
from generators.knitting.base_knitter import BaseKnitter
from qiskit.converters import (
    circuit_to_dag,
    dag_to_circuit
)
from qiskit.dagcircuit import DAGCircuit
from qiskit import (
    QuantumRegister,
    ClassicalRegister,
)
from qiskit.circuit import (
    Qubit,
    Clbit,
)
from uuid import uuid4

"""Module with a generator strategy that combines quantum circuits in parallel.

In parallel means that that the two circuits are combined by acting on disjoint
sets of qubits and classical bits. The resulting circuit will have a size equal
to the sum of the sizes of the input circuits.

This module contains the following functions:
- parallel_combine_circuits: Combine two quantum circuits in parallel.

"""


class ParallelKnitter(BaseKnitter):
    def __init__(
        self,
        circuit1: QuantumCircuit,
        circuit2: QuantumCircuit,
        sanitizers: Optional[List[Callable]] = None,
        sanitizers_only_circuit1: Optional[List[Callable]] = None,
        sanitizers_only_circuit2: Optional[List[Callable]] = None,
    ) -> None:
        super().__init__(circuit1=circuit1, circuit2=circuit2)
        self.sanitizers = sanitizers or []
        self.sanitizers_only_circuit1 = sanitizers_only_circuit1 or []
        self.sanitizers_only_circuit2 = sanitizers_only_circuit2 or []

    def combine_circuits(self) -> QuantumCircuit:
        """Combine two quantum circuits in parallel.

        This method takes two quantum circuits and combines them into a single
        quantum circuit by placing them in parallel. The resulting circuit will
        have all the quantum and classical registers from both circuits, with
        unique names to avoid conflicts.

        Steps:

        1. Convert both input circuits to DAG (Directed Acyclic Graph)
           representations.

        2. Create a new empty DAGCircuit.

        3. Generate unique prefixes for the registers of each input circuit to
           ensure no name conflicts.

        4. Add quantum and classical registers from both circuits to the new
           DAGCircuit with the unique prefixes.

        5. Iterate through the operations of both DAG circuits, update their
           register names with the unique prefixes, and add them to the new
           DAGCircuit.

        6. Convert the combined DAGCircuit back to a QuantumCircuit.

        Returns:
            QuantumCircuit: A new quantum circuit that combines the operations
            of self.circuit1 and self.circuit2 in parallel.

        """
        dag_circuit1 = circuit_to_dag(self.circuit1)
        dag_circuit2 = circuit_to_dag(self.circuit2)
        new_dag = DAGCircuit()
        prefix_circuit1 = str(uuid4())[:6]
        prefix_circuit2 = str(uuid4())[:6]
        reference_to_registers = self._create_reference_to_registers(
            qregs=self.circuit1.qregs,
            cregs=self.circuit1.cregs,
            prefix=prefix_circuit1,
            new_dag=new_dag
        )
        reference_to_registers.update(self._create_reference_to_registers(
            qregs=self.circuit2.qregs,
            cregs=self.circuit2.cregs,
            prefix=prefix_circuit2,
            new_dag=new_dag
        ))

        for prefix, dag_circuit in zip(
            [prefix_circuit1, prefix_circuit2],
                [dag_circuit1, dag_circuit2]):
            for node in dag_circuit.topological_op_nodes():
                new_qargs = self._replace_register_names(
                    node.qargs,
                    reference_to_registers,
                    prefix
                )
                new_cargs = self._replace_register_names(
                    node.cargs,
                    reference_to_registers,
                    prefix
                )
                if node.op._condition is not None:
                    new_conditions = self._replace_register_names(
                        [node.op._condition[0]],
                        reference_to_registers,
                        prefix
                    )
                    node.op._condition = (
                        new_conditions[0],
                        node.op._condition[1],
                    )
                # print("=" * 80)
                # print(f"Processing node from circuit with prefix {prefix}")
                # print("op name: ", node.op.name)
                # print("Original qargs: ", node.qargs)
                # print("Original cargs: ", node.cargs)
                # print("new_qargs: ", new_qargs)
                # print("new_cargs: ", new_cargs)
                new_dag.apply_operation_back(node.op, new_qargs, new_cargs)

        combined_qc = dag_to_circuit(new_dag)
        return combined_qc
