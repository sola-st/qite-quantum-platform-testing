OPENQASM 2.0;
include "qelib1.inc";

qreg a[2];
qreg b[2];
qreg cin[1];
cx a[0],b[0];
