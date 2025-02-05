import os
import json
import random
from typing import Dict, Any
import traceback
import time
import uuid
from pathlib import Path
import logging
from enum import Enum


class CrashType(Enum):
    IMPORTER_CRASH = "importer_crash"
    EXPORTER_CRASH = "exporter_crash"
    TRANSFORMER_CRASH = "transformer_crash"
    GENERIC_CRASH = "generic_crash"


class QasmSelector:
    def __init__(self, previous_picks=None, picking_strategy=None):
        self.previous_picks = previous_picks or {}
        self.picking_strategy = picking_strategy

    def pick(self, folder):
        qasm_files = [f for f in os.listdir(folder) if f.endswith('.qasm')]
        qasm_file = random.choice(qasm_files)  # Simplified picking strategy
        return os.path.join(folder, qasm_file)


class Operation:
    def __init__(self, name):
        self.name = name
        self.current_status = {}
        self.raise_any_exception = False

    def load_current_status(self, status: Dict[str, Any]):
        self.current_status = status
        self.input_base_qasm_name = Path(status.get("input_qasm")).stem

    def execute(self):
        raise NotImplementedError

    def run(
            self, *args, **kwargs):
        try:
            return self.execute(*args, **kwargs)
        except Exception as e:
            if self.raise_any_exception:
                raise e
            else:
                if "'NoneType' object has no attribute 'n_gates_of_type'" in str(e):
                    breakpoint()
                self.log_error({
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": time.time(),
                    "crashing_operation": self.name,
                    **self.current_status
                })
                return CrashType.GENERIC_CRASH

    def log_error(self, error_info):
        uuid_str = uuid.uuid4().hex[:6]
        log_path = os.path.join(
            self.error_folder,
            f"{self.input_base_qasm_name}_{uuid_str}_error.json")
        with open(log_path, 'w') as f:
            json.dump(error_info, f, indent=4)

    def set_exception_handling(self, raise_any_exception: bool):
        self.raise_any_exception = raise_any_exception

    def set_folders(self, metadata_folder, error_folder):
        self.metadata_folder = metadata_folder
        self.error_folder = error_folder


class Transformer(Operation):
    def __init__(self, transformer_name):
        super().__init__(transformer_name)

    def execute(self, qc_obj, *args, **kwargs):
        return self.transform(qc_obj, *args, **kwargs)

    def transform(self, qc_obj):
        raise NotImplementedError


class Importer(Operation):
    def __init__(self, importer_name):
        super().__init__(importer_name)

    def execute(self, path, *args, **kwargs):
        return self.import_qasm(path, *args, **kwargs)

    def import_qasm(self, path):
        raise NotImplementedError


class Exporter(Operation):
    def __init__(self, exporter_name):
        super().__init__(exporter_name)

    def execute(self, qc_obj, path, *args, **kwargs):
        return self.export(qc_obj, path, *args, **kwargs)

    def export(self, qc_obj, path):
        raise NotImplementedError


# Set up module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler and set level to debug
ch = logging.StreamHandler()
# ch.setLevel(logging.CRITICAL)
ch.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
logger.addHandler(ch)


class PlatformProcessor:
    def __init__(self, metadata_folder, error_folder, output_folder):
        self._importer = None
        self.transformers = []
        self._exporter = None
        self.name = "base_class_processor"
        self.metadata_folder = metadata_folder
        self.error_folder = error_folder
        self.output_folder = output_folder

    def set_importer(self, importer):
        self._importer = importer
        logger.info(f"Importer set: {importer}")

    def add_transformer(self, transformer):
        self.transformers.append(transformer)
        logger.info(f"Transformer added: {transformer}")

    def set_exporter(self, exporter):
        self._exporter = exporter
        logger.info(f"Exporter set: {exporter}")

    def set_exception_handling(self, raise_any_exception: bool):
        """Iterates over all operations and sets the raise_any_exception attribute."""
        operations = {
            self._importer, *self.transformers, self._exporter}
        for operation in operations:
            operation.set_exception_handling(raise_any_exception)
        logger.info(f"Exception handling set to: {raise_any_exception}")

    def set_folders(self, metadata_folder, error_folder):
        """Sets the metadata and error folders for all operations."""
        operations = {
            self._importer, *self.transformers, self._exporter}
        for operation in operations:
            operation.set_folders(metadata_folder, error_folder)
        logger.info(
            f"Metadata folder set to: {metadata_folder}, Error folder set to: {error_folder}")

    def execute_qite_loop(self, qasm_file, raise_any_exception: bool = False):
        logger.info(f"Executing QITE loop with QASM file: {qasm_file}")
        self.current_status = {
            "input_qasm": qasm_file,
            "platform": self.name,
            "importer_function": None,
            "transformer_functions": [],
            "exporter_function": None,
        }

        random_id = uuid.uuid4().hex[:6]
        prefix_qasm_file = os.path.basename(qasm_file).split("_")[0]
        base_output_name = f"{prefix_qasm_file}_qite_{random_id}"
        qasm_output_filename = f"{base_output_name}.qasm"
        metadata_output_filename = f"{base_output_name}.json"

        self.set_exception_handling(raise_any_exception)
        self.set_folders(
            metadata_folder=self.metadata_folder,
            error_folder=self.error_folder)

        logger.info(
            f"current_status: {json.dumps(self.current_status, indent=4)}")
        qc = self._handle_import(qasm_file)
        if isinstance(qc, CrashType):
            logger.info("Import failed, stopping QITE on this program")
            return None

        self.current_status["transformer_functions"] = []
        for transformer in self.transformers:
            self.current_status["transformer_functions"].append(
                transformer.name)
            transformer.load_current_status(self.current_status)
            qc = transformer.run(qc)
            if isinstance(qc, CrashType):
                logger.info(
                    f"Transfor {transformer} failed, stopping QITE on this program")
                return None
            logger.info(f"Transformer {transformer} applied")

        export_path = self._handle_export(
            qc, exported_filename=qasm_output_filename)
        if isinstance(export_path, CrashType):
            logger.info("Export failed, stopping QITE on this program")
            return None

        # store provenance metadata
        metadata_path = os.path.join(
            self.metadata_folder, metadata_output_filename)
        with open(metadata_path, 'w') as f:
            json.dump(self.current_status, f, indent=4)
        logger.info(f"Metadata stored at: {metadata_path}")

        return export_path

    def _handle_import(self, qasm_file):
        self._importer.load_current_status(self.current_status)
        qc = self._importer.run(qasm_file)
        self.current_status["importer_function"] = self._importer.name
        logger.info(f"QASM file imported: {qasm_file}")
        return qc

    def _handle_export(self, qc, exported_filename=None):
        self._exporter.load_current_status(self.current_status)
        export_path = self._exporter.run(
            qc_obj=qc,
            path=self.output_folder,
            filename=exported_filename)
        self.current_status["exporter_function"] = self._exporter.name
        self.current_status["output_qasm"] = export_path
        logger.info(f"QASM file exported to: {export_path}")
        return export_path
