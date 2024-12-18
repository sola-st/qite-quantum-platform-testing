OPENQASM 2.0;
include "qelib1.inc";
gate cs q0,q1 { p(pi/4) q0; cx q0,q1; p(-pi/4) q1; cx q0,q1; p(pi/4) q1; }
gate rzx(param0) q0,q1 { h q1; cx q0,q1; rz(param0) q1; cx q0,q1; h q1; }
gate ecr q0,q1 { rzx(pi/4) q0,q1; x q0; rzx(-pi/4) q0,q1; }
qreg q[5];
cz q[4],q[2];
rccx q[1],q[0],q[3];
rccx q[0],q[2],q[3];
swap q[4],q[1];
cswap q[0],q[1],q[4];
rx(1.4036081019556235) q[2];
cp(1.861607263265477) q[2],q[1];
cs q[4],q[0];
cy q[0],q[1];
cswap q[2],q[3],q[4];
ch q[2],q[3];
cswap q[0],q[1],q[4];
ecr q[0],q[3];
rccx q[4],q[2],q[1];
ch q[2],q[0];
rccx q[3],q[4],q[1];
cswap q[2],q[3],q[1];
cy q[4],q[0];
rccx q[1],q[3],q[0];
