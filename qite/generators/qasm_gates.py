from dataclasses import dataclass
from typing import Callable
import random
import math


@dataclass
class Gate:
    name: str
    num_qubits: int
    num_params: int = 0
    sanitize_params: Callable = lambda x: x

    def to_qasm(self, qreg_name: str, circuit_size: int) -> str:
        qubits = random.sample(range(circuit_size), self.num_qubits)
        qubit_str = ",".join(f"{qreg_name}[{q}]" for q in qubits)
        if self.num_params > 0:
            params = [
                self.sanitize_params(random.uniform(0, 2 * math.pi))
                for _ in range(self.num_params)]
            param_str = ",".join(map(str, params))
            return f"{self.name}({param_str}) {qubit_str};"
        else:
            return f"{self.name} {qubit_str};"


class U3(Gate):
    def __init__(self):
        super().__init__("u3", 1, 3)


class U2(Gate):
    def __init__(self):
        super().__init__("u2", 1, 2)


class U1(Gate):
    def __init__(self):
        super().__init__("u1", 1, 1)


class CX(Gate):
    def __init__(self):
        super().__init__("cx", 2)


class ID(Gate):
    def __init__(self):
        super().__init__("id", 1)


class U0(Gate):
    def __init__(self):
        super().__init__("u0", 1, 1, lambda x: math.ceil(x))


class U(Gate):
    def __init__(self):
        super().__init__("u", 1, 3)


class P(Gate):
    def __init__(self):
        super().__init__("p", 1, 1)


class X(Gate):
    def __init__(self):
        super().__init__("x", 1)


class Y(Gate):
    def __init__(self):
        super().__init__("y", 1)


class Z(Gate):
    def __init__(self):
        super().__init__("z", 1)


class H(Gate):
    def __init__(self):
        super().__init__("h", 1)


class S(Gate):
    def __init__(self):
        super().__init__("s", 1)


class SDG(Gate):
    def __init__(self):
        super().__init__("sdg", 1)


class T(Gate):
    def __init__(self):
        super().__init__("t", 1)


class TDG(Gate):
    def __init__(self):
        super().__init__("tdg", 1)


class RX(Gate):
    def __init__(self):
        super().__init__("rx", 1, 1)


class RY(Gate):
    def __init__(self):
        super().__init__("ry", 1, 1)


class RZ(Gate):
    def __init__(self):
        super().__init__("rz", 1, 1)


class SX(Gate):
    def __init__(self):
        super().__init__("sx", 1)


class SXDG(Gate):
    def __init__(self):
        super().__init__("sxdg", 1)


class CZ(Gate):
    def __init__(self):
        super().__init__("cz", 2)


class CY(Gate):
    def __init__(self):
        super().__init__("cy", 2)


class SWAP(Gate):
    def __init__(self):
        super().__init__("swap", 2)


class CH(Gate):
    def __init__(self):
        super().__init__("ch", 2)


class CCX(Gate):
    def __init__(self):
        super().__init__("ccx", 3)


class CSWAP(Gate):
    def __init__(self):
        super().__init__("cswap", 3)


class CRX(Gate):
    def __init__(self):
        super().__init__("crx", 2, 1)


class CRY(Gate):
    def __init__(self):
        super().__init__("cry", 2, 1)


class CRZ(Gate):
    def __init__(self):
        super().__init__("crz", 2, 1)


class CU1(Gate):
    def __init__(self):
        super().__init__("cu1", 2, 1)


class CP(Gate):
    def __init__(self):
        super().__init__("cp", 2, 1)


class CU3(Gate):
    def __init__(self):
        super().__init__("cu3", 2, 3)


class CSX(Gate):
    def __init__(self):
        super().__init__("csx", 2)


class CU(Gate):
    def __init__(self):
        super().__init__("cu", 2, 4)


class RXX(Gate):
    def __init__(self):
        super().__init__("rxx", 2, 1)


class RZZ(Gate):
    def __init__(self):
        super().__init__("rzz", 2, 1)


class RCCX(Gate):
    def __init__(self):
        super().__init__("rccx", 3)


class RC3X(Gate):
    def __init__(self):
        super().__init__("rc3x", 4)


class C3X(Gate):
    def __init__(self):
        super().__init__("c3x", 4)


class C3SQRTX(Gate):
    def __init__(self):
        super().__init__("c3sqrtx", 4)


class C4X(Gate):
    def __init__(self):
        super().__init__("c4x", 5)


GATE_MAP = {
    "u3": U3(),
    "u2": U2(),
    "u1": U1(),
    "cx": CX(),
    "id": ID(),
    "u0": U0(),
    "u": U(),
    "p": P(),
    "x": X(),
    "y": Y(),
    "z": Z(),
    "h": H(),
    "s": S(),
    "sdg": SDG(),
    "t": T(),
    "tdg": TDG(),
    "rx": RX(),
    "ry": RY(),
    "rz": RZ(),
    "sx": SX(),
    "sxdg": SXDG(),
    "cz": CZ(),
    "cy": CY(),
    "swap": SWAP(),
    "ch": CH(),
    "ccx": CCX(),
    "cswap": CSWAP(),
    "crx": CRX(),
    "cry": CRY(),
    "crz": CRZ(),
    "cu1": CU1(),
    "cp": CP(),
    "cu3": CU3(),
    "csx": CSX(),
    "cu": CU(),
    "rxx": RXX(),
    "rzz": RZZ(),
    "rccx": RCCX(),
    "rc3x": RC3X(),
    "c3x": C3X(),
    "c3sqrtx": C3SQRTX(),
    "c4x": C4X()}
