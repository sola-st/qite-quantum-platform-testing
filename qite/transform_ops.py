from validate.qiskit_processor import (
    QiskitChangeGateSetU3CX, QiskitOptimizerLevel2
)

from qite.transforms.pytket_transforms import list_pytket_transformers

all_transform_ops = [
    QiskitChangeGateSetU3CX(),
    QiskitOptimizerLevel2(),
    *list_pytket_transformers
]

transform_lookup = {
    op.name: op for op in all_transform_ops
}
