OPENQASM 2.0;
include "qelib1.inc";
qreg q[11];
creg c[11];
id q[0];
id q[1];
id q[2];
id q[3];
id q[4];
id q[5];
id q[6];
id q[7];
id q[8];
id q[9];
id q[10];
u2(0,pi) q[2];
u2(0,pi) q[4];
cx q[9],q[2];
u1(-pi/4) q[2];
cx q[7],q[2];
u1(pi/4) q[2];
cx q[9],q[2];
u1(-pi/4) q[2];
cx q[7],q[2];
u1(pi/4) q[2];
u2(0,pi) q[2];
u2(0,pi) q[2];
cx q[4],q[2];
u1(0.688059) q[2];
cx q[4],q[2];
u2(0,pi) q[2];
u2(0,pi) q[4];
u1(pi/4) q[9];
cx q[7],q[9];
u1(pi/4) q[7];
u1(-pi/4) q[9];
cx q[7],q[9];
u2(0,pi) q[10];
cx q[6],q[10];
u1(-pi/4) q[10];
cx q[1],q[10];
u1(pi/4) q[10];
cx q[6],q[10];
u1(-pi/4) q[10];
cx q[1],q[10];
u1(pi/4) q[10];
u2(0,pi) q[10];
u3(0,-0.3528898750000001,-0.3528898750000001) q[10];
cx q[3],q[10];
u3(0,-2.788702778589793,3.4944825285897934) q[10];
u2(0,pi) q[10];
u1(pi/4) q[6];
cx q[1],q[6];
u1(pi/4) q[1];
u1(-pi/4) q[6];
cx q[1],q[6];
cx q[6],q[10];
u1(-pi/4) q[10];
cx q[1],q[10];
u1(pi/4) q[10];
cx q[6],q[10];
u1(-pi/4) q[10];
cx q[1],q[10];
u1(pi/4) q[10];
u2(0,pi) q[10];
u3(0,-0.3528898750000001,-0.3528898750000001) q[10];
cx q[3],q[10];
u3(0,-2.788702778589793,3.4944825285897934) q[10];
u1(pi/4) q[6];
cx q[1],q[6];
u1(pi/4) q[1];
u1(-pi/4) q[6];
cx q[1],q[6];
u1(-pi/2) q[1];
u2(0,pi) q[1];
u1(-pi/2) q[1];
cx q[6],q[8];
h q[6];
cx q[8],q[6];
tdg q[6];
cx q[3],q[6];
t q[6];
cx q[8],q[6];
tdg q[6];
cx q[3],q[6];
t q[6];
h q[6];
t q[8];
cx q[3],q[8];
t q[3];
tdg q[8];
cx q[3],q[8];
cx q[6],q[8];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
measure q[7] -> c[7];
measure q[8] -> c[8];
measure q[9] -> c[9];
measure q[10] -> c[10];
