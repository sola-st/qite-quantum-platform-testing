from validate.qiskit_processor import (
    QiskitChangeGateSetU3CX, QiskitOptimizerLevel2
)

from validate.pytket_processor import (
    PytketOptimizerPeephole
)


all_transform_ops = [
    QiskitChangeGateSetU3CX(),
    QiskitOptimizerLevel2(),
    PytketOptimizerPeephole()
]

transform_lookup = {
    op.name: op for op in all_transform_ops
}
