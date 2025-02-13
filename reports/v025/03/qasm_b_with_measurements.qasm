OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
swap q[1],q[2];
measure q[1] -> c[1];
measure q[2] -> c[2];