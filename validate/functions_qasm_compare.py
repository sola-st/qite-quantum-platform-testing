

def compare_qasm_via_qcec(path_qasm_a: str, path_qasm_b: str) -> None:
    """Compare two QASM files using QCEC."""
    from mqt import qcec
    result = qcec.verify(str(path_qasm_a), str(path_qasm_b))
    equivalence = str(result.equivalence)
    if (
            equivalence == 'equivalent' or
            equivalence == 'equivalent_up_to_global_phase'
    ):
        print(f"The circuits are equivalent: {path_qasm_a}, {path_qasm_b}")
        return
    raise ValueError(
        f"The circuits are not equivalent: {path_qasm_a}, {path_qasm_b}")


# def compare_qasm_via_pyzx(path_qasm_a: str, path_qasm_b: str) -> None:
#     """Compare two QASM files using PyZX."""
#     import pyzx as zx
#     circ_a = zx.Circuit.from_qasm_file(path_qasm_a)
#     circ_b = zx.Circuit.from_qasm_file(path_qasm_b)
#     equivalent_demonstrated = circ_a.verify_equality(circ_b)
#     if equivalent_demonstrated:
#         print(f"The circuits are equivalent: {path_qasm_a}, {path_qasm_b}")
#         return
#     raise ValueError(
#         f"The circuits may be not equivalent: {path_qasm_a}, {path_qasm_b}")
