OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];
creg c[4];
cx q[0],q[1];
cx q[1],q[0];
cx q[0],q[1];
measure q[1] -> c[0];
cx q[1],q[3];
cx q[3],q[1];
cx q[1],q[3];
cx q[0],q[1];
cx q[1],q[0];
cx q[0],q[1];
cx q[3],q[1];
measure q[3] -> c[0];
