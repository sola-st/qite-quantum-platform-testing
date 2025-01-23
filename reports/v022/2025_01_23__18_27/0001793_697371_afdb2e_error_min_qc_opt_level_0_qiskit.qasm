OPENQASM 2.0;
include "qelib1.inc";
gate iswap q0,q1 { s q0; s q1; h q0; cx q0,q1; cx q1,q0; h q1; }
qreg qr[11];
creg cr[11];
ccx qr[6],qr[7],qr[10];
u3(0,-0.5215388750000001,-0.5215388750000001) qr[10];
cx qr[5],qr[10];
u3(0,-2.620053778589793,-2.620053778589793) qr[10];
ccx qr[6],qr[7],qr[10];
u3(0,-0.5215388750000001,-0.5215388750000001) qr[10];
cx qr[5],qr[10];
u3(0,-2.620053778589793,-2.620053778589793) qr[10];
t qr[5];
iswap qr[10],qr[5];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
measure qr[3] -> cr[3];
measure qr[4] -> cr[4];
measure qr[5] -> cr[5];
measure qr[6] -> cr[6];
measure qr[7] -> cr[7];
measure qr[8] -> cr[8];
measure qr[9] -> cr[9];
measure qr[10] -> cr[10];
