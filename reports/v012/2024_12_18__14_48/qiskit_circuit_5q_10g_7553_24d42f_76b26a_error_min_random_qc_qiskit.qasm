OPENQASM 2.0;
include "qelib1.inc";
gate r(param0,param1) q0 { u3(param0,param1 - pi/2,pi/2 - param1) q0; }
gate iswap q0,q1 { s q0; s q1; h q0; cx q0,q1; cx q1,q0; h q1; }
qreg q[5];
s q[0];
r(5.396314340880207,6.093408752738254) q[4];
z q[1];
iswap q[3],q[2];
p(5.648536112355301) q[2];
c3sqrtx q[1],q[0],q[4],q[3];
u1(6.238362454909296) q[1];
cswap q[0],q[4],q[3];
p(4.110937123771645) q[1];
c3sqrtx q[0],q[2],q[3],q[4];
t q[4];
c3sqrtx q[1],q[2],q[3],q[0];
