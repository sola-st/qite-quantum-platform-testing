from qite.transforms.pytket_transforms import list_pytket_transformers
from qite.transforms.qiskit_transforms import list_qiskit_transformers
from qite.transforms.pennylane_transforms import list_pennylane_transformers
from qite.transforms.bqskit_transforms import list_bqskit_transformers

all_transform_ops = [
    *list_pytket_transformers,
    *list_qiskit_transformers,
    *list_pennylane_transformers,
    *list_bqskit_transformers,
]

transform_lookup = {
    op.name: op for op in all_transform_ops
}
