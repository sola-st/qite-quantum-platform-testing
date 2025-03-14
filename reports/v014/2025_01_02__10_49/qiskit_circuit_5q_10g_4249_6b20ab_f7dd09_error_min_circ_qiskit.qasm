OPENQASM 2.0;
include "qelib1.inc";
opaque delay(param0) q0;
qreg q[6];
creg c[6];
delay(1.0) q[4];
