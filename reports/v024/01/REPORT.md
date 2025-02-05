# Title: Rebase Issue: `u0` Gate Not Removed with `AutoRebase`
## Versions
```
pytket version: 1.33.1
qiskit version: 1.2.4
```

## Expected behavior
The `u0` gate should be converting to something else when rebasing the circuit to use another gate set compatible with the `GreedyPauliSimp` pass.

## Actual behavior
When creating a circuit with the `u0` gate (standard gate included in `qelib1.inc`) and trying to rebase it to use another gate set (compatible with the `GreedyPauliSimp` pass), the `u0` gate is converted to a `u3` gate (which is not in the target gateset). In particular, that makes the circuit incompatible with the `GreedyPauliSimp` pass, which expects the target gateset instead and raises a `RuntimeError`.

## Additional information
This issue reproduces consistently. The `u0` gate is incorrectly converted to `u3` (not in the target gate set) even after applying the `AutoRebase`, and `GreedyPauliSimp` passes raise a `RuntimeError` due to the gate set mismatch.

## Source code
```python
qasm_content = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
u0(5) q[0];
u3 (0.0, 0.4, 0.0) q[1];
"""
from pytket.circuit.display import render_circuit_jupyter
from pytket.qasm import (
    circuit_from_qasm_str, circuit_to_qasm_str
)

tk_circuit = circuit_from_qasm_str(qasm_content)

# Rebase
from pytket.passes import (
    GreedyPauliSimp,
    AutoRebase,
)

from pytket.circuit import OpType
allowed_ops = {
    OpType.PhasedX, OpType.Measure, OpType.ZZMax,
    OpType.Tdg, OpType.T, OpType.Ry, OpType.Rx, OpType.Z, OpType.X,
    OpType.PauliExpBox, OpType.Rz, OpType.Y, OpType.S, OpType.Sdg,
    OpType.V, OpType.Vdg, OpType.SWAP, OpType.H, OpType.YYPhase,
    OpType.CY, OpType.XXPhase, OpType.CX, OpType.ZZPhase, OpType.CZ
}
AutoRebase(allowed_ops).apply(tk_circuit)

qasm_content = circuit_to_qasm_str(tk_circuit)
print(qasm_content)
# OPENQASM 2.0;
# include "qelib1.inc";

# qreg q[2];
# u3(0.0*pi,0.0*pi,0.0*pi) q[0];
# rz(0.12732395447351627*pi) q[1];

GreedyPauliSimp().apply(tk_circuit)

qasm_content = circuit_to_qasm_str(tk_circuit)
print(qasm_content)

# RuntimeError: Predicate requirements are not satisfied: GateSetPredicate:{ PhasedX Measure PhaseGadget ZZMax Tdg T Ry Rx Z X PauliExpBox Rz Y S Sdg V Vdg SWAP H YYPhase CY XXPhase CX ZZPhase CZ }
```

Let me know if you need any more information. Thanks in advance!