
import os
from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import load, dump
from validate.platform_processor import (
    PlatformProcessor, Importer, Transformer, Exporter
)


class QiskitProcessor(PlatformProcessor):
    def __init__(self, metadata_folder, error_folder, output_folder):
        super().__init__(
            metadata_folder, error_folder, output_folder)
        self.set_importer(QiskitImporter())
        self.set_exporter(QiskitExporter())
        self.name = "qiskit"


class QiskitImporter(Importer):
    def __init__(self):
        super().__init__("qiskit_import")

    def import_qasm(self, path):
        try:
            # raise Exception("Optimizer failed")
            qc = load(path)
            return qc
        except Exception as e:
            raise e


class QiskitOptimizerLevel2(Transformer):
    def __init__(self):
        super().__init__("optimizer_lvl2")

    def transform(self, qc_obj):
        return transpile(qc_obj, optimization_level=2)


class QiskitChangeGateSetU3CX(Transformer):
    def __init__(self):
        super().__init__("change_gateset_u3_cx")

    def transform(self, qc_obj):
        return transpile(qc_obj, basis_gates=['u3', 'cx'])


class QiskitExporter(Exporter):
    def __init__(self):
        super().__init__("qiskit_export")

    def export(self, qc_obj, path, filename="exported.qasm"):
        try:
            qasm_path = os.path.join(path, filename)
            dump(qc_obj, qasm_path)
            return qasm_path
        except Exception as e:
            raise e
