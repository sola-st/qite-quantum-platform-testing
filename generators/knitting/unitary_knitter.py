from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Operator
from generators.knitting.base_knitter import BaseKnitter
from qiskit.converters import circuit_to_dag
from generators.knitting.sanitizers import (
    RemoveMeasurementsSanitizer,
    AssignRandomParamsSanitizer,
    DropConditionedOperationsSanitizer,
)
from copy import deepcopy

"""
Unitary Embedding: Convert qc1 into a unitary operation and embed it as a unitary gate
within qc2.

This function takes a quantum circuit (qc1), converts it into a unitary operation,
and embeds it as a unitary gate within another quantum circuit (qc2).

Args:
    qc1 (QuantumCircuit): The quantum circuit to be converted into a unitary operation.
    qc2 (QuantumCircuit): The quantum circuit where the unitary gate will be embedded.

Returns:
    QuantumCircuit: The modified quantum circuit qc2 with the embedded unitary gate.
"""


class UnitaryKnitter(BaseKnitter):

    def _inject_as_unitary(self, source_circuit: QuantumCircuit,
                           target_circuit: QuantumCircuit) -> None:
        """Inject the unitary operation of the source circuit into the target.

        This method sanitizes the source circuit by removing measurements, converts it into a unitary operator,
        and appends this operator to the target circuit.

        Args:
            source_circuit (QuantumCircuit): The quantum circuit from which the unitary operation is derived.
            target_circuit (QuantumCircuit): The quantum circuit to which the unitary operation is appended.

        Returns:
            None
        """
        sanitizers = [
            RemoveMeasurementsSanitizer(),
            AssignRandomParamsSanitizer(),
            DropConditionedOperationsSanitizer()
        ]
        for sanitizer in sanitizers:
            source_circuit = sanitizer.sanitize(source_circuit)

        self.prefix1 = None
        self.prefix2 = None

        # print("Sanitized source circuit: ")
        # print(source_circuit)
        unitary_operator = Operator(source_circuit)
        # print("Unitary operator: ")
        # print(unitary_operator)
        instruction_unitary = unitary_operator.to_instruction()
        instruction_unitary.label = "Injected Unitary"
        n_qubits_operator = source_circuit.num_qubits
        target_qubits = target_circuit.qubits[:n_qubits_operator]
        target_circuit.append(instruction_unitary, target_qubits)

    def combine_circuits(self) -> QuantumCircuit:
        """Combine circuit1 and circuit2 into a single circuit."""
        total_num_qubits = max(self.circuit1.num_qubits,
                               self.circuit2.num_qubits)
        total_num_clbits = max(self.circuit1.num_clbits,
                               self.circuit2.num_clbits)
        qreg_combined = QuantumRegister(total_num_qubits, name="qreg")
        creg_combined = ClassicalRegister(total_num_clbits, name="creg")
        combined_circuit = QuantumCircuit(qreg_combined, creg_combined)
        self._inject_as_unitary(self.circuit1, combined_circuit)
        combined_circuit.compose(
            self.circuit2, qreg_combined[: self.circuit2.num_qubits],
            creg_combined[: self.circuit2.num_clbits], inplace=True)

        print("Combined circuit: ")
        print(combined_circuit)

        # create viz DAG
        self.combine_dag = circuit_to_dag(combined_circuit)
        all_qregs = combined_circuit.qregs
        all_cregs = combined_circuit.cregs
        # add registers to viz DAG
        for qreg in all_qregs:
            self.viz_dag.add_qreg(qreg)
        for creg in all_cregs:
            self.viz_dag.add_creg(creg)
        # reference to register
        all_registers = all_qregs + all_cregs
        reference_to_registers = {
            reg.name: reg for reg in all_registers
        }
        reference_to_registers.update({
            "2_" + reg.name: reg for reg in all_registers
        })

        # print("Reference to registers: ")
        # print(reference_to_registers)

        for node in self.combine_dag.topological_op_nodes():
            new_node = deepcopy(node)
            if node.op.label and node.op.label.startswith("Injected Unitary"):
                self._apply_operation_viz(
                    node=new_node,
                    prefix="1",
                    reference_to_registers=reference_to_registers,
                    apply_register_renaming=False
                )
            else:
                self._apply_operation_viz(
                    node=new_node,
                    prefix="2",
                    reference_to_registers=reference_to_registers,
                    apply_register_renaming=False
                )

        return combined_circuit
