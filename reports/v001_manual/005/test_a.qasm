OPENQASM 2.0;
include "qelib1.inc";
gate ms(param0) q0,q1,q2 { rxx(0.844396) q0,q1; rxx(0.844396) q0,q2; rxx(0.844396) q1,q2; }
qreg qr[3];
creg cr[3];
ms(1) qr[2],qr[1],qr[0];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];