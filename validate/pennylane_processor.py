import os
import pennylane as qml
from pennylane.tape import make_qscript, QuantumScript
from validate.platform_processor import PlatformProcessor, Importer, Exporter


class PennyLaneProcessor(PlatformProcessor):
    def __init__(self, metadata_folder, error_folder, output_folder):
        super().__init__(metadata_folder, error_folder, output_folder)
        self.set_importer(PennyLaneImporter())
        self.set_exporter(PennyLaneExporter())
        self.name = "pennylane"


class PennyLaneImporter(Importer):
    def __init__(self):
        super().__init__("pennylane_import")

    def import_qasm(self, path):
        try:
            with open(path, 'r') as f:
                qasm_content = f.read()
            circuit = qml.from_qasm(qasm_content)
            return circuit
        except Exception as e:
            raise e


class PennyLaneExporter(Exporter):
    def __init__(self):
        super().__init__("pennylane_export")

    def export(self, circuit, path, filename="exported.qasm"):
        try:
            from pennylane.transforms import decompose
            dec_circuit = decompose(
                circuit, {qml.RX, qml.RY, qml.RZ, qml.CNOT, qml.CZ})
            qasm_str = self._export_to_qasm_with_pennylane(dec_circuit)
            qasm_path = os.path.join(path, filename)
            with open(qasm_path, 'w') as f:
                f.write(qasm_str)
            return qasm_path
        except Exception as e:
            raise e

    def _export_to_qasm_with_pennylane(self, circuit):
        """Export a PennyLane circuit to a QASM file."""
        qs = make_qscript(circuit)()
        new_ops = []
        wires_to_measure = set()
        for op in qs:
            if op.name == 'MidMeasureMP':
                for wire in op.wires.tolist():
                    wires_to_measure.add(wire)
            else:
                new_ops.append(op)
        qs_no_meas = QuantumScript(
            new_ops,
            [qml.expval(qml.PauliZ(wire)) for wire in wires_to_measure]
        )

        qasm_str_pennylane = qs_no_meas.to_openqasm(measure_all=True)
        return qasm_str_pennylane
