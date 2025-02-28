include "qelib1.inc";
qreg q[11];
c4x q[5],q[8],q[9],q[2],q[3];
c4x q[10],q[1],q[8],q[0],q[9];
u0(4) q[3];