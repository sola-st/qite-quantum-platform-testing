from qiskit import QuantumCircuit
from typing import List, Callable, Optional, Union, Dict, Tuple
from generators.knitting.base_knitter import BaseKnitter
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.dagcircuit import DAGCircuit
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.circuit import Qubit, Clbit
from uuid import uuid4
from generators.knitting.sanitizers import AnonymizeRegistersSanitizer

"""Module with a generator strategy that combines quantum circuits sequentially.

This module contains the following functions:
- sequential_combine_circuits: Combine two quantum circuits sequentially.

"""


class SequentialKnitter(BaseKnitter):

    def combine_circuits(self) -> QuantumCircuit:
        """Combine two quantum circuits sequentially.

        This method takes two quantum circuits and combines them into a single
        quantum circuit by placing them sequentially. The resulting circuit will
        have all the quantum and classical registers from both circuits, with
        unique names to avoid conflicts.

        Returns:
            QuantumCircuit: A new quantum circuit that combines the operations
            of self.circuit1 and self.circuit2 sequentially.
        """
        total_num_qubits = max(self.circuit1.num_qubits,
                               self.circuit2.num_qubits)
        total_num_clbits = max(self.circuit1.num_clbits,
                               self.circuit2.num_clbits)
        qreg_combined = QuantumRegister(total_num_qubits, name="qreg")
        creg_combined = ClassicalRegister(total_num_clbits, name="creg")
        combined_circuit = QuantumCircuit(qreg_combined, creg_combined)

        # anonymize both circuits
        anonimizer = AnonymizeRegistersSanitizer()
        self.circuit1 = anonimizer.sanitize(self.circuit1)
        self.circuit2 = anonimizer.sanitize(self.circuit2)

        dag_circuit1 = circuit_to_dag(self.circuit1)
        dag_circuit2 = circuit_to_dag(self.circuit2)
        new_dag = DAGCircuit()
        reference_to_registers = {}
        self.prefix1 = "1"
        self.prefix2 = "2"

        # map any reference to the two existing registers
        # map all quantum registers from both circuits to the combined register
        reference_to_registers.update({
            qreg.name: qreg_combined
            for qreg in self.circuit1.qregs + self.circuit2.qregs
        })
        # map all classical registers from both circuits to the combined register
        reference_to_registers.update({
            creg.name: creg_combined
            for creg in self.circuit1.cregs + self.circuit2.cregs
        })

        # print("reference_to_registers", reference_to_registers)

        # initialize registers for the viz DAG
        new_dag.add_qreg(qreg_combined)
        new_dag.add_creg(creg_combined)
        self.viz_dag.add_qreg(qreg_combined)
        self.viz_dag.add_creg(creg_combined)

        for prefix, dag_circuit in zip(
                [self.prefix1, self.prefix2], [dag_circuit1, dag_circuit2]):
            # print("=" * 80)
            # print("prefix", prefix)
            for node in dag_circuit.topological_op_nodes():
                new_op, new_qregs, new_cregs = self._remap_op_to_new_registers(
                    node=node,
                    reference_to_registers=reference_to_registers,
                )
                new_dag.apply_operation_back(
                    new_op, qargs=new_qregs, cargs=new_cregs)

                # print(dag_to_circuit(new_dag))

                # add fake ops in the viz DAG
                new_fake_op, new_qregs, new_cregs = self._remap_op_to_new_registers(
                    node=node,
                    reference_to_registers=reference_to_registers,
                    viz_subscript=prefix,
                    viz_color="red" if prefix == self.prefix1 else "blue",
                    viz_add_as_fake=True,
                )
                self.viz_dag.apply_operation_back(
                    new_fake_op, qargs=new_qregs, cargs=new_cregs)

        combined_circuit = dag_to_circuit(new_dag)
        return combined_circuit
