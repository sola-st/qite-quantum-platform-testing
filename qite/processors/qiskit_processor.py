
import os
from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import (
    load, dump, LEGACY_CUSTOM_INSTRUCTIONS
)
from qite.processors.platform_processor import (
    PlatformProcessor
)
from qite.base.primitives import (
    Importer, Transformer, Exporter
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
            qc = load(path, custom_instructions=LEGACY_CUSTOM_INSTRUCTIONS)
            return qc
        except Exception as e:
            raise e


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
