OPENQASM 2.0;
include "qelib1.inc";
gate ms(param0) q0,q1,q2 { rxx(0.414823) q0,q1; rxx(0.414823) q0,q2; rxx(0.414823) q1,q2; }
gate rzx(param0) q0,q1 { h q1; cx q0,q1; rz(param0) q1; cx q0,q1; h q1; }
gate dcx q0,q1 { cx q0,q1; cx q1,q0; }
qreg qr[5];
creg cr[5];
ms(0.414823) qr[2],qr[1],qr[3];
ccx qr[1],qr[2],qr[4];
rzx(0.817247) qr[0],qr[3];
measure qr[2] -> cr[2];
dcx qr[0],qr[2];
id qr[1];
rz(4.672516) qr[4];
measure qr[1] -> cr[4];
y qr[0];
p(3.805937) qr[2];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
measure qr[3] -> cr[3];
measure qr[4] -> cr[4];
