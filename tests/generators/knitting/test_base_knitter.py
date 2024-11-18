import pytest
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from generators.knitting.parallel_knitter import ParallelKnitter
from generators.knitting.interleaved_knitter import InterleavedKnitter
from generators.knitting.unitary_knitter import UnitaryKnitter
from pathlib import Path
import tempfile
import filecmp


@pytest.fixture
def qc_1():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.z(0).c_if(qc.cregs[0], 1)
    return qc


@pytest.fixture
def qc_2():
    qc = QuantumCircuit(2, 2)
    qc.cz(0, 1)
    qc.y(0)
    return qc


# def test_combine_circuits_parallel(qc_1, qc_2):
#     """
#     Test that the combine_circuits method correctly combines two quantum circuits.
#     """
#     pk = ParallelKnitter(qc_1, qc_2)
#     qc_combine = pk.combine_circuits()

#     qc_viz = pk.get_viz_circuit()
#     assert qc_viz is not None, "The visualized circuit should not be None"

#     displaytext = pk.get_viz_map_name_to_text()
#     displaycolor = pk.get_viz_map_name_to_color()

#     expected_image = Path(
#         'tests/artifacts/viz/combined_circuit_parallel.png')

#     with tempfile.TemporaryDirectory() as tmpdirname:
#         temp_output_path = Path(tmpdirname) / 'combined_circuit.png'
#         qc_viz.draw("mpl",
#                     style={
#                         "displaytext": displaytext,
#                         "displaycolor": displaycolor},
#                     filename=temp_output_path)

#         assert filecmp.cmp(
#             temp_output_path, expected_image), "The generated image does not match the expected image"


# def test_combine_circuits_interleaved(qc_1, qc_2):
#     """
#     Test that the combine_circuits method correctly combines two quantum circuits using InterleavedKnitter.
#     """
#     ik = InterleavedKnitter(qc_1, qc_2)
#     qc_combine_interleaved = ik.combine_circuits()

#     qc_viz_interleaved = ik.get_viz_circuit()
#     assert qc_viz_interleaved is not None, "The visualized circuit should not be None"

#     displaytext_interleaved = ik.get_viz_map_name_to_text()
#     displaycolor_interleaved = ik.get_viz_map_name_to_color()

#     expected_image_interleaved = Path(
#         'tests/artifacts/viz/combined_circuit_interleaved.png')

#     with tempfile.TemporaryDirectory() as tmpdirname:
#         temp_output_path_interleaved = Path(
#             tmpdirname) / 'combined_circuit_interleaved.png'
#         qc_viz_interleaved.draw(
#             "mpl",
#             style={"displaytext": displaytext_interleaved,
#                    "displaycolor": displaycolor_interleaved},
#             filename=temp_output_path_interleaved)
#         assert filecmp.cmp(temp_output_path_interleaved,
#                            expected_image_interleaved), "The generated image does not match the expected image"


# def test_combine_circuits_unitary(qc_1, qc_2):
#     """
#     Test that the combine_circuits method correctly combines two quantum circuits using UnitaryKnitter.
#     """
#     uk = UnitaryKnitter(qc_1, qc_2)
#     qc_combine_unitary = uk.combine_circuits()

#     qc_viz_unitary = uk.get_viz_circuit()
#     assert qc_viz_unitary is not None, "The visualized circuit should not be None"

#     displaytext_unitary = uk.get_viz_map_name_to_text()
#     displaycolor_unitary = uk.get_viz_map_name_to_color()

#     expected_image_unitary = Path(
#         'tests/artifacts/viz/combined_circuit_unitary.png')

#     with tempfile.TemporaryDirectory() as tmpdirname:
#         temp_output_path_unitary = Path(
#             tmpdirname) / 'combined_circuit_unitary.png'
#         qc_viz_unitary.draw(
#             "mpl",
#             style={"displaytext": displaytext_unitary,
#                    "displaycolor": displaycolor_unitary},
#             filename=temp_output_path_unitary)
#         assert filecmp.cmp(temp_output_path_unitary,
#                            expected_image_unitary), "The generated image does not match the expected image"


def test_combine_circuits_with_c_if():
    """
    Test combining qc_1 with a circuit that has a c_if z gate.
    """
    qc_1 = QuantumCircuit(2, 2)
    qc_1.h(0)
    qc_1.cx(0, 1)
    qc_1.z(0).c_if(qc_1.cregs[0], 1)

    qreg = QuantumRegister(2, 'myq')
    creg = ClassicalRegister(3, 'myc')
    qc_3 = QuantumCircuit(qreg, creg)
    qc_3.cz(0, 1)
    qc_3.z(1).c_if(creg[2], 1)

    print("QC1:\n", qc_1)
    print("QC3:\n", qc_3)

    uk = UnitaryKnitter(qc_1, qc_3)
    qc_combine = uk.combine_circuits()

    qc_viz = uk.get_viz_circuit()
    assert qc_viz is not None, "The visualized circuit should not be None"

    displaytext = uk.get_viz_map_name_to_text()
    displaycolor = uk.get_viz_map_name_to_color()

    expected_image = Path(
        'tests/artifacts/viz/combined_circuit_with_c_if.png')

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_output_path = Path(tmpdirname) / 'combined_circuit_with_c_if.png'
        qc_viz.draw("mpl",
                    style={
                        "displaytext": displaytext,
                        "displaycolor": displaycolor},
                    filename=temp_output_path)

        assert filecmp.cmp(
            temp_output_path, expected_image), "The generated image does not match the expected image"
