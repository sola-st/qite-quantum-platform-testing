from bqskit import compile as bqskit_compile
from qite.base.primitives import Transformer


class BQSKitOptimizer(Transformer):
    def __init__(self, optimization_level):
        super().__init__(f"bqskit_optimizer_level_{optimization_level}")
        self.optimization_level = optimization_level

    def transform(self, circuit):
        compiled_circuit = bqskit_compile(
            circuit, optimization_level=self.optimization_level)
        return compiled_circuit


list_bqskit_transformers = [
    BQSKitOptimizer(1),
    BQSKitOptimizer(2),
    BQSKitOptimizer(3),
]
