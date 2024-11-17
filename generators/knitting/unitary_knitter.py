from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from generators.knitting.base_knitter import BaseKnitter
from generators.knitting.sanitizers import (
    RemoveMeasurementsSanitizer,
    AssignRandomParamsSanitizer,
    DropConditionedOperationsSanitizer,
)

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

        print("Sanitized source circuit: ")
        print(source_circuit)
        unitary_operator = Operator(source_circuit)
        # print("Unitary operator: ")
        # print(unitary_operator)
        n_qubits_operator = source_circuit.num_qubits
        target_qubits = target_circuit.qubits[:n_qubits_operator]
        target_circuit.append(unitary_operator, target_qubits)

    def combine_circuits(self) -> QuantumCircuit:
        """Combine circuit1 and circuit2 into a single circuit."""
        total_num_qubits = self.circuit1.num_qubits + self.circuit2.num_qubits
        total_num_clbits = self.circuit1.num_clbits + self.circuit2.num_clbits
        combined_circuit = QuantumCircuit(total_num_qubits, total_num_clbits)
        self._inject_as_unitary(self.circuit1, combined_circuit)
        combined_circuit.compose(self.circuit2, inplace=True)
        return combined_circuit
