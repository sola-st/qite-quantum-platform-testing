OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg cr[2];
creg cr[2];
measure q[0] -> cr[0];
measure q[1] -> cr[1];
