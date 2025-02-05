from pytket.passes import (
    FullPeepholeOptimise, PeepholeOptimise2Q, RemoveRedundancies,
    EulerAngleReduction, KAKDecomposition, CliffordPushThroughMeasures,
    FlattenRegisters, PauliSimp, GreedyPauliSimp,
    AutoRebase,
    OptimisePhaseGadgets,
    ZXGraphlikeOptimisation
)
from pytket.circuit import OpType
from validate.platform_processor import Transformer


class PytketOptimizerFullPeephole(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_full_peephole")

    def transform(self, tk_circuit):
        FullPeepholeOptimise().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerPeephole2Q(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_peephole_2q")

    def transform(self, tk_circuit):
        PeepholeOptimise2Q().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerRemoveRedundancies(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_remove_redundancies")

    def transform(self, tk_circuit):
        RemoveRedundancies().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerEulerAngleReduction(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_euler_angle_reduction")

    def transform(self, tk_circuit):
        EulerAngleReduction(q=OpType.Rz, p=OpType.Rx).apply(tk_circuit)
        return tk_circuit


class PytketOptimizerKAKDecomposition(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_kak_decomposition")

    def transform(self, tk_circuit):
        KAKDecomposition().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerCliffordPushThroughMeasures(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_clifford_push_through_measures")

    def transform(self, tk_circuit):
        CliffordPushThroughMeasures().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerFlattenRegisters(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_flatten_registers")

    def transform(self, tk_circuit):
        FlattenRegisters().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerPauliSimp(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_pauli_simp")

    def transform(self, tk_circuit):
        allowed_ops = {
            OpType.PhasedX, OpType.Measure, OpType.ZZMax,
            OpType.Tdg, OpType.T, OpType.Ry, OpType.Rx, OpType.Z, OpType.X,
            OpType.PauliExpBox, OpType.Rz, OpType.Y, OpType.S, OpType.Sdg,
            OpType.V, OpType.Vdg, OpType.SWAP, OpType.H, OpType.YYPhase,
            OpType.CY, OpType.XXPhase, OpType.CX, OpType.ZZPhase, OpType.CZ
        }
        AutoRebase(allowed_ops).apply(tk_circuit)
        PauliSimp().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerGreedyPauliSimp(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_greedy_pauli_simp")

    def transform(self, tk_circuit):
        allowed_ops = {
            OpType.PhasedX, OpType.Measure, OpType.ZZMax,
            OpType.Tdg, OpType.T, OpType.Ry, OpType.Rx, OpType.Z, OpType.X,
            OpType.PauliExpBox, OpType.Rz, OpType.Y, OpType.S, OpType.Sdg,
            OpType.V, OpType.Vdg, OpType.SWAP, OpType.H, OpType.YYPhase,
            OpType.CY, OpType.XXPhase, OpType.CX, OpType.ZZPhase, OpType.CZ
        }
        AutoRebase(allowed_ops).apply(tk_circuit)
        GreedyPauliSimp().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerOptimisePhaseGadgets(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_optimise_phase_gadgets")

    def transform(self, tk_circuit):
        OptimisePhaseGadgets().apply(tk_circuit)
        return tk_circuit


class PytketOptimizerZXGraphlikeOptimisation(Transformer):
    def __init__(self):
        super().__init__("pytket_optimizer_zx_graphlike_optimisation")

    def transform(self, tk_circuit):
        allowed_ops = {
            OpType.CX, OpType.Z, OpType.CZ, OpType.Rx, OpType.H, OpType.X,
            OpType.Rz, OpType.SWAP, OpType.noop,
        }
        AutoRebase(allowed_ops).apply(tk_circuit)
        ZXGraphlikeOptimisation().apply(tk_circuit)
        return tk_circuit


class PytketChangeGateSet(Transformer):
    def __init__(self):
        super().__init__("change_gateset")

    def transform(self, tk_circuit):
        # Assuming the gate set change is handled by some optimization pass
        # Here we just return the circuit as is
        return tk_circuit


list_pytket_transformers = [
    PytketOptimizerFullPeephole(),
    PytketOptimizerPeephole2Q(),
    PytketOptimizerRemoveRedundancies(),
    PytketOptimizerEulerAngleReduction(),
    PytketOptimizerKAKDecomposition(),
    PytketOptimizerCliffordPushThroughMeasures(),
    PytketOptimizerFlattenRegisters(),
    PytketOptimizerPauliSimp(),
    PytketOptimizerGreedyPauliSimp(),
    PytketOptimizerOptimisePhaseGadgets(),
    PytketOptimizerZXGraphlikeOptimisation()
]
