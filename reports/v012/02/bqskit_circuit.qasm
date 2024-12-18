OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
cs q[4], q[0];
