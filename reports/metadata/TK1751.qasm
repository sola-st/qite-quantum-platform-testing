OPENQASM 2.0;
include "qelib1.inc";

gate yyphase (param0) yyphaseq0,yyphaseq1 {
u3(0.0*pi,1.5*pi,0.0*pi) yyphaseq0;
cx yyphaseq1,yyphaseq0;
u3((param0/pi)*pi,0.0*pi,0.0*pi) yyphaseq1;
cx yyphaseq1,yyphaseq0;
u3(0.0*pi,1.5*pi,1.0*pi) yyphaseq0;
}
qreg qr[11];
creg cr[11];
measure qr[3] -> cr[3];
measure qr[6] -> cr[6];
measure qr[7] -> cr[7];
measure qr[10] -> cr[10];
c4x qr[0],qr[5],qr[2],qr[9];
yyphase(1.8851890276839556*pi) qr[8],qr[1];
y qr[4];
measure qr[0] -> cr[0];
measure qr[1] -> cr[1];
measure qr[2] -> cr[2];
measure qr[4] -> cr[4];
measure qr[5] -> cr[5];
measure qr[8] -> cr[8];
measure qr[9] -> cr[9];