import os
import json
from typing import Dict, Any
import traceback
import time
import uuid
from pathlib import Path
from enum import Enum


class CrashType(Enum):
    IMPORTER_CRASH = "importer_crash"
    EXPORTER_CRASH = "exporter_crash"
    TRANSFORMER_CRASH = "transformer_crash"
    GENERIC_CRASH = "generic_crash"


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
