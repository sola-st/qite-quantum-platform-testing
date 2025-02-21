import os
from bqskit import Circuit
from bqskit.passes import QuickPartitioner, ScanningGateRemovalPass, UnfoldPass
from bqskit import compile as bqskit_compile


from qite.processors.platform_processor import PlatformProcessor
from qite.base.primitives import Importer, Transformer, Exporter


class BQSKitProcessor(PlatformProcessor):
    def __init__(self, metadata_folder, error_folder, output_folder):
        super().__init__(metadata_folder, error_folder, output_folder)
        self.set_importer(BQSKitImporter())
        self.set_exporter(BQSKitExporter())
        self.name = "bqskit"


class BQSKitImporter(Importer):
    def __init__(self):
        super().__init__("bqskit_import")

    def import_qasm(self, path):
        try:
            circuit = self._import_from_qasm_with_bqskit(path)
            return circuit
        except Exception as e:
            raise e

    def _import_from_qasm_with_bqskit(self, file_path: str):
        """Import a QASM file using BQSKit."""
        circuit = Circuit.from_file(file_path)
        return circuit


class BQSKitExporter(Exporter):
    def __init__(self):
        super().__init__("bqskit_export")

    def export(self, circuit, path, filename="exported.qasm"):
        try:
            qasm_path = self._export_to_qasm_with_bqskit(
                circuit, path, filename)
            return qasm_path
        except Exception as e:
            raise e

    def _export_to_qasm_with_bqskit(self, circuit, path, filename):
        """Export a BQSKit circuit to a QASM file."""
        file_path = os.path.join(path, filename)
        circuit.save(file_path)
        return file_path
