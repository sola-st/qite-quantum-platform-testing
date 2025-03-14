OPENQASM 2.0;
include "qelib1.inc";
qreg qr[2];
creg cr[2];
h qr[0];
s qr[0];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];