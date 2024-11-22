OPENQASM 2.0;
include "qelib1.inc";
qreg reg_1_q[5];
qreg reg_2_q[4];
creg reg_2_c[4];
measure reg_2_q[0] -> reg_2_c[0];
h reg_2_q[0];
