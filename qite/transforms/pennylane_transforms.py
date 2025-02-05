from validate.platform_processor import Transformer
import pennylane as qml

from pennylane.transforms import (
    cancel_inverses,
    commute_controlled,
    merge_rotations,
    single_qubit_fusion,
    unitary_to_rot,
    merge_amplitude_embedding,
    remove_barrier,
    undo_swaps,
    # pattern_matching_optimization,
    decompose,
    combine_global_phases,
    clifford_t_decomposition,
    defer_measurements,
)


class PennylaneOptimizerCancelInverses(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_cancel_inverses")

    def transform(self, circuit):
        new_circuit = cancel_inverses(circuit)
        return new_circuit


class PennylaneOptimizerCommuteControlled(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_commute_controlled")

    def transform(self, circuit):
        new_circuit = commute_controlled(circuit)
        return new_circuit


class PennylaneOptimizerMergeRotations(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_merge_rotations")

    def transform(self, circuit):
        new_circuit = merge_rotations(circuit)
        return new_circuit


class PennylaneOptimizerSingleQubitFusion(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_single_qubit_fusion")

    def transform(self, circuit):
        new_circuit = single_qubit_fusion(circuit)
        return new_circuit


class PennylaneOptimizerUnitaryToRot(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_unitary_to_rot")

    def transform(self, circuit):
        new_circuit = unitary_to_rot(circuit)
        return new_circuit


class PennylaneOptimizerMergeAmplitudeEmbedding(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_merge_amplitude_embedding")

    def transform(self, circuit):
        new_circuit = merge_amplitude_embedding(circuit)
        return new_circuit


class PennylaneOptimizerRemoveBarrier(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_remove_barrier")

    def transform(self, circuit):
        new_circuit = remove_barrier(circuit)
        return new_circuit


class PennylaneOptimizerUndoSwaps(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_undo_swaps")

    def transform(self, circuit):
        new_circuit = undo_swaps(circuit)
        return new_circuit


class PennylaneOptimizerDecompose(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_decompose")

    def transform(self, circuit):
        new_circuit = decompose(circuit)
        return new_circuit


class PennylaneOptimizerCombineGlobalPhases(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_combine_global_phases")

    def transform(self, circuit):
        new_circuit = combine_global_phases(circuit)
        return new_circuit


class PennylaneOptimizerCliffordTDecomposition(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_clifford_t_decomposition")

    def transform(self, circuit):
        new_circuit = clifford_t_decomposition(circuit)
        return new_circuit


class PennylaneOptimizerDeferMeasurements(Transformer):
    def __init__(self):
        super().__init__("pennylane_optimizer_defer_measurements")

    def transform(self, circuit):
        new_circuit = defer_measurements(circuit)
        return new_circuit


list_pennylane_transformers = [
    PennylaneOptimizerCancelInverses(),
    PennylaneOptimizerCommuteControlled(),
    PennylaneOptimizerMergeRotations(),
    PennylaneOptimizerSingleQubitFusion(),
    PennylaneOptimizerUnitaryToRot(),
    PennylaneOptimizerMergeAmplitudeEmbedding(),
    PennylaneOptimizerRemoveBarrier(),
    PennylaneOptimizerUndoSwaps(),
    PennylaneOptimizerDecompose(),
    PennylaneOptimizerCombineGlobalPhases(),
    # PennylaneOptimizerCliffordTDecomposition(),
    PennylaneOptimizerDeferMeasurements(),
]
