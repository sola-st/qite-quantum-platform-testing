OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg reg_2_c[2];
measure q[0] -> reg_2_c[0];
h q[1];
