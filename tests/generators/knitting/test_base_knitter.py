import pytest
from qiskit import QuantumCircuit
from generators.knitting.parallel_knitter import ParallelKnitter
from pathlib import Path
import tempfile
import filecmp


def test_combine_circuits():
    """
    Test that the combine_circuits method correctly combines two quantum circuits.
    """
    qc_1 = QuantumCircuit(2, 2)
    qc_1.h(0)
    qc_1.cx(0, 1)
    qc_1.z(0).c_if(qc_1.cregs[0], 1)

    qc_2 = QuantumCircuit(2, 2)
    qc_2.cz(0, 1)
    qc_2.y(0)

    pk = ParallelKnitter(qc_1, qc_2)
    qc_combine = pk.combine_circuits()

    qc_viz = pk.get_viz_circuit()
    assert qc_viz is not None, "The visualized circuit should not be None"

    displaytext = pk.get_viz_map_name_to_text()
    displaycolor = pk.get_viz_map_name_to_color()

    expected_image = Path('tests/artifacts/viz/combined_circuit_parallel.png')

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_output_path = Path(tmpdirname) / 'combined_circuit.png'
        qc_viz.draw("mpl",
                    style={
                        "displaytext": displaytext,
                        "displaycolor": displaycolor},
                    filename=temp_output_path)

        assert filecmp.cmp(
            temp_output_path, expected_image), "The generated image does not match the expected image"
