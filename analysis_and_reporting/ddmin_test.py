import analysis_and_reporting.ddmin as dd
import sys
import os
import tempfile
import pathlib
import uuid
from validate.parse_qasm2 import _execute_in_docker, _compose_docker_command_qiskit


def test_ddmin():
    def repro_func(lst_steps):
        """A Test function should return False if it reproduces
            In this case we're just looking for any combination of
            the letters e or f that is greater than 2
        """
        if ((lst_steps.count('e') + lst_steps.count('f')) >= 2):
            return False
        else:
            return True

    # The circumstances is an iterable and separable list of steps or conditions
    circumstances = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

    debugger = dd.DDMin(circumstances, repro_func)
    assert debugger.execute() == ['e', 'f']
    # run it again, with an odd number of elements
    debugger = dd.DDMin(circumstances[:-1], repro_func)
    assert debugger.execute() == ['e', 'f']
    print("Test passed")


def test_qasm():
    def repro_func(lst_steps):
        """A Test function should return False if it reproduces
            In this case we're just looking for any combination of
            the letters e or f that is greater than 2
        """
        qasm_content = "\n".join(lst_steps)
        fixed_header = "OPENQASM 2.0;\ninclude \"qelib1.inc\";"
        qasm_content = fixed_header + "\n" + qasm_content
        # breakpoint()
        # write tmp file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = pathlib.Path(temp_dir) / f"{uuid.uuid4()}.qasm"
            with open(temp_file_path, 'w') as f:
                f.write(qasm_content)
            res, error_msg = _execute_in_docker(
                image_name="qiskit_runner",
                command=_compose_docker_command_qiskit(
                    qasm_file=temp_file_path),
                input_folder=pathlib.Path(temp_dir),
            )
            if error_msg:
                print(error_msg)
                if "\\'u\\' is not defined in this scope" in str(error_msg):
                    return False
            return True

        # qasm2.load("qiskit_circuit_5q_10g_5_1c2586_qc_qiskit.qasm")

        # if ((lst_steps.count('e') + lst_steps.count('f')) >= 2):
        #     return False
        # else:
        #     return True

    # The circumstances is an iterable and separable list of steps or conditions
    # circumstances = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    qasm_file = "program_bank/2024_09_23__17_19__qiskit/qiskit_circuit_5q_10g_8_6a77d4_isa_qc_qiskit.qasm"
    qasm_content = open(qasm_file).read()
    qasm_statements = qasm_content.split("\n")
    # remove the header
    qasm_statements = qasm_statements[2:]
    print(qasm_statements)

    debugger = dd.DDMin(qasm_statements, repro_func)
    min_version = debugger.execute()
    fixed_header = "OPENQASM 2.0;\ninclude \"qelib1.inc\";"
    min_program = "\n".join(min_version)
    min_program = fixed_header + "\n" + min_program
    print(min_program)
    assert min_version == ['gate mcphase(param0) q0,q1,q2,q3 { u(pi/2,0,pi) q3; cx q1,q3; p(-pi/4) q3; cx q0,q3; p(pi/4) q3; cx q1,q3; p(pi/4) q1; p(-pi/4) q3; cx q0,q3; cx q0,q1; p(pi/4) q0; p(-pi/4) q1; cx q0,q1; u(pi/2,-0.23561425000000025,-3*pi/4) q3; cx q2,q3; u(pi/2,0,-2.905978403589792) q3; cx q1,q3; p(-pi/4) q3; cx q0,q3; p(pi/4) q3; cx q1,q3; p(pi/4) q1; p(-pi/4) q3; cx q0,q3; cx q0,q1; p(pi/4) q0; p(-pi/4) q1; cx q0,q1; u(pi/2,-0.23561425000000025,-3*pi/4) q3; cx q2,q3; u(0,-3.023785528589793,-3.0237855285897925) q3; cx q0,q2; u(0,-0.05890356249999984,-0.05890356249999984) q2; cx q1,q2; u(0,-3.0826890910897933,-3.0826890910897937) q2; cx q0,q2; u(0,-0.05890356249999984,-0.05890356249999984) q2; cx q1,q2; u(0,-3.0826890910897933,-3.0826890910897937) q2; u(0,0,0.117807125) q1; cx q0,q1; u(0,0,-0.117807125) q1; cx q0,q1; p(0.117807125) q0; }']
    # # run it again, with an odd number of elements
    # debugger = dd.DDMin(qasm_statements[:-1], repro_func)
    # assert debugger.execute() == ['e', 'f']


if __name__ == '__main__':
    # test_ddmin()
    test_qasm()
