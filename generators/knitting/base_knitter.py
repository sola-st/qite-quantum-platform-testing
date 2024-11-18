from pathlib import Path
from typing import Any, List, Optional, Dict, Tuple, Union, Callable
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.dagcircuit import DAGCircuit, DAGOpNode
from qiskit import QuantumRegister, ClassicalRegister
from qiskit.circuit import Qubit, Clbit
from uuid import uuid4
from copy import deepcopy


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
        self,
        circuit1: QuantumCircuit,
        circuit2: QuantumCircuit,
        prefix1: str = "1",
        prefix2: str = "2",
        sanitizers: Optional[List[Callable]] = None,
        sanitizers_only_circuit1: Optional[List[Callable]] = None,
        sanitizers_only_circuit2: Optional[List[Callable]] = None,
    ) -> None:
        """Initialize the BaseKnitter object."""
        self.circuit1 = circuit1
        self.circuit2 = circuit2
        self.prefix1 = prefix1
        self.prefix2 = prefix2
        self.sanitizers = sanitizers or []
        self.sanitizers_only_circuit1 = sanitizers_only_circuit1 or []
        self.sanitizers_only_circuit2 = sanitizers_only_circuit2 or []
        self.viz_dag = DAGCircuit()
        self.viz_map_name_to_text = {}
        self.viz_map_name_to_color = {}

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

    def _remap_registers(
            self,
            register_to_map: Tuple[
                Union[Qubit, Clbit, QuantumRegister, ClassicalRegister]],
            mapping_old_name_to_register: Dict[
                str, Union[QuantumRegister, ClassicalRegister]]
    ) -> Tuple[Union[Qubit, Clbit, QuantumRegister, ClassicalRegister]]:
        """Remap the registers to the new ones."""
        new_registers = []
        for register in register_to_map:
            if isinstance(register, (QuantumRegister, ClassicalRegister)):
                new_registers.append(
                    mapping_old_name_to_register
                    [register.name])
            elif isinstance(register, (Qubit, Clbit)):
                new_register = mapping_old_name_to_register[register._register.name]
                new_registers.append(new_register[register._index])
        return tuple(new_registers)

    def _rename_registers(
        self,
        prefix: str,
        registers: List[Union[QuantumRegister, ClassicalRegister]],
    ) -> List[Union[QuantumRegister, ClassicalRegister]]:
        """Rename the registers of a circuit."""
        new_registers = []
        for reg in registers:
            new_name = f"{prefix}_{reg.name}"
            if isinstance(reg, QuantumRegister):
                new_reg = QuantumRegister(reg.size, new_name)
            elif isinstance(reg, ClassicalRegister):
                new_reg = ClassicalRegister(reg.size, new_name)
            new_registers.append(new_reg)
        return new_registers

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

    def _remap_op_to_new_registers(
            self, node: DAGOpNode,
            reference_to_registers: Dict[
                str, Union[QuantumRegister, ClassicalRegister]],
            viz_subscript: str = None,
            viz_color: str = None,
            viz_add_as_fake: bool = False
        ) -> Tuple[
            DAGOpNode,
            List[Union[Qubit, Clbit, QuantumRegister, ClassicalRegister]],
            List[Union[Qubit, Clbit, QuantumRegister, ClassicalRegister]]]:
        """Remap the operation to the new registers.

        This method replaces any occurrences of registers or quantum/classical bits
        in the operation with the new ones provided in the reference_to_registers mapping.

        Args:
            node (DAGOpNode): The operation node to be remapped.
            reference_to_registers
                A dictionary mapping the original register names to the new registers.
            viz_subscript (str, optional): An optional subscript to be added to the operation's name
                for visualization purposes. Defaults to None.
            viz_color (str, optional): An optional color to be associated with the operation's name
                for visualization purposes. If provided, viz_subscript must also be provided. Defaults to None.

        Returns:
            A tuple containing the remapped operation node, the list of new quantum arguments, and the list of new classical arguments.
        """
        if viz_subscript:
            standard_node_name = f"{node.op.name}_{viz_subscript}"
            latex_name = node.op.name + "_{" + viz_subscript + "}"
        else:
            standard_node_name = node.op.name
            latex_name = node.op.name
        if viz_add_as_fake:
            qc_fake = QuantumCircuit(1, name=standard_node_name)
            qc_fake.x(0)
            fake_op = qc_fake.to_instruction()
            new_op = deepcopy(fake_op)
        else:
            new_op = deepcopy(node.op)
        new_qargs = self._remap_registers(node.qargs, reference_to_registers)
        new_cargs = self._remap_registers(node.cargs, reference_to_registers)
        if node.op._condition is not None:
            new_conditions = self._remap_registers(
                [node.op._condition[0]],
                reference_to_registers
            )
            new_op._condition = (
                new_conditions[0],
                node.op._condition[1],
            )
        if viz_subscript:
            self.viz_map_name_to_text[standard_node_name] = latex_name
            if viz_color:
                self.viz_map_name_to_color[standard_node_name] = viz_color
        else:
            if viz_color:
                print("Warning: Viz color provided without subscript.")
        return new_op, new_qargs, new_cargs

    def _apply_operation(
            self, node: DAGOpNode,
            prefix: str,
            reference_to_registers:
            Dict
            [Union[QuantumRegister, ClassicalRegister],
             Union[QuantumRegister, ClassicalRegister]],
            new_dag: DAGCircuit) -> None:
        """Apply an operation to the DAG with updated register names."""
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
        new_op = deepcopy(node.op)
        if node.op._condition is not None:
            new_conditions = self._replace_register_names(
                [new_op._condition[0]],
                reference_to_registers,
                prefix
            )
            new_op._condition = (
                new_conditions[0],
                node.op._condition[1],
            )
        new_dag.apply_operation_back(new_op, new_qargs, new_cargs)

    def _apply_operation_viz(
        self,
        node: DAGOpNode,
        prefix: str,
        reference_to_registers: Dict[str, Union[QuantumRegister, ClassicalRegister]],
        apply_register_renaming: bool = True,
    ) -> None:
        """Apply an operation to the DAG with updated register names.

        Assume that the register names have already been updated by the
        normal apply operation function.
        """
        new_qargs = node.qargs
        new_cargs = node.cargs
        if apply_register_renaming:
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
        # create a fake circuit to visualize the DAG
        new_name = f"{node.op.name}_{prefix}"
        new_name_latex = node.op.name + "_{" + prefix + "}"
        self.viz_map_name_to_text[new_name] = new_name_latex
        self.viz_map_name_to_color[new_name] = "red" if prefix.startswith(
            "1") else "blue"
        qc_fake = QuantumCircuit(1, name=new_name)
        qc_fake.x(0)
        custom_gate = qc_fake.to_instruction()
        if node.op._condition is not None:
            new_conditions = self._replace_register_names(
                [node.op._condition[0]],
                reference_to_registers,
                prefix
            )
            custom_gate._condition = (
                new_conditions[0],
                node.op._condition[1],
            )
        self.viz_dag.apply_operation_back(custom_gate, new_qargs, new_cargs)

    def get_viz_circuit(self) -> QuantumCircuit:
        """Get the visualization circuit."""
        return dag_to_circuit(self.viz_dag)

    def get_viz_map_name_to_text(self) -> Dict[str, str]:
        """Get the visualization map name to text."""
        return dict(self.viz_map_name_to_text)

    def get_viz_map_name_to_color(self) -> Dict[str, str]:
        """Get the visualization map name to color."""
        return dict(self.viz_map_name_to_color)
