import os
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit
from pytket.qasm import (
    circuit_from_qasm_str, circuit_to_qasm_str
)
from qite.processors.platform_processor import (
    PlatformProcessor
)
from qite.base.primitives import (
    Importer, Exporter, Converter
)


class PytketProcessor(PlatformProcessor):
    def __init__(self, metadata_folder, error_folder, output_folder):
        super().__init__(
            metadata_folder, error_folder, output_folder)
        self.set_importer(PytketImporter())
        self.set_exporter(PytketExporter())
        self.set_converter(PytketConverter())
        self.name = "pytket"


class PytketImporter(Importer):
    def __init__(self):
        super().__init__("pytket_import")

    def import_qasm(self, path):
        try:
            with open(path, 'r') as f:
                qasm_content = f.read()
            tk_circuit = circuit_from_qasm_str(qasm_content)
            return tk_circuit
        except Exception as e:
            raise e


class PytketExporter(Exporter):
    def __init__(self):
        super().__init__("pytket_export")

    def export(self, tk_circuit, path, filename="exported.qasm"):
        try:
            qasm_str = circuit_to_qasm_str(tk_circuit)
            qasm_path = os.path.join(path, filename)
            with open(qasm_path, 'w') as f:
                f.write(qasm_str)
            return qasm_path
        except Exception as e:
            raise e


class PytketConverter(Converter):
    def __init__(self):
        super().__init__("pytket_convert")

    def convert(self, qc_qiskit, *args, **kwargs):
        """Convert a Qiskit QuantumCircuit to a Pytket Circuit."""
        try:
            tk_circuit = qiskit_to_tk(qc_qiskit)
            return tk_circuit
        except Exception as e:
            raise e
