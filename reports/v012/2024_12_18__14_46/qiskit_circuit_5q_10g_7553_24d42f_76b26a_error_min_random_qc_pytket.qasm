OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];
u3(0.0*pi,0.0*pi,0.5*pi) q[0];
u3(0.0*pi,0.0*pi,1.0*pi) q[1];
u1(0.5*pi) q[2];
u1(0.5*pi) q[3];
u3(1.717700203657537*pi,1.4395922465554285*pi,0.5604077534445715*pi) q[4];
u1(0.06249999999999997*pi) q[1];
u2(0.0*pi,1.0*pi) q[3];
cx q[3],q[2];
cx q[2],q[3];
u2(0.0*pi,1.0*pi) q[2];
u2(0.0*pi,1.0*pi) q[3];
cx q[1],q[3];
u3(0.0*pi,0.0*pi,1.797984887028847*pi) q[2];
u1(1.9375*pi) q[3];
cx q[1],q[3];
cx q[1],q[0];
u1(0.06249999999999997*pi) q[3];
u1(1.9375*pi) q[0];
u2(0.0*pi,1.0*pi) q[3];
u2(0.0*pi,1.0*pi) q[3];
cx q[0],q[3];
u1(0.06249999999999997*pi) q[3];
cx q[0],q[3];
cx q[1],q[0];
u1(1.9375*pi) q[3];
u1(0.06249999999999997*pi) q[0];
u2(0.0*pi,1.0*pi) q[3];
u2(0.0*pi,1.0*pi) q[3];
cx q[0],q[3];
u1(1.9375*pi) q[3];
cx q[0],q[3];
cx q[0],q[4];
u1(0.06249999999999997*pi) q[3];
u2(0.0*pi,1.0*pi) q[3];
u1(1.9375*pi) q[4];
u2(0.0*pi,1.0*pi) q[3];
cx q[4],q[3];
u1(0.06249999999999997*pi) q[3];
cx q[4],q[3];
cx q[1],q[4];
u1(1.9375*pi) q[3];
u2(0.0*pi,1.0*pi) q[3];
u1(0.06249999999999997*pi) q[4];
u2(0.0*pi,1.0*pi) q[3];
cx q[4],q[3];
u1(1.9375*pi) q[3];
cx q[4],q[3];
cx q[0],q[4];
u1(0.06249999999999997*pi) q[3];
u2(0.0*pi,1.0*pi) q[3];
u1(1.9375*pi) q[4];
u2(0.0*pi,1.0*pi) q[3];
cx q[4],q[3];
u1(0.06249999999999997*pi) q[3];
cx q[4],q[3];
cx q[1],q[4];
u1(1.9375*pi) q[3];
u3(0.0*pi,0.0*pi,1.9857324429954124*pi) q[1];
u2(0.0*pi,1.0*pi) q[3];
u1(0.06249999999999997*pi) q[4];
u3(0.0*pi,0.0*pi,1.3085519279764737*pi) q[1];
u2(0.0*pi,1.0*pi) q[3];
u1(0.06249999999999997*pi) q[1];
cx q[4],q[3];
u1(1.9375*pi) q[3];
cx q[4],q[3];
u1(0.06249999999999997*pi) q[3];
u2(0.0*pi,1.0*pi) q[3];
cx q[3],q[4];
h q[3];
cx q[4],q[3];
tdg q[3];
cx q[0],q[3];
t q[3];
cx q[4],q[3];
tdg q[3];
t q[4];
cx q[0],q[3];
cx q[0],q[4];
t q[3];
t q[0];
h q[3];
tdg q[4];
cx q[0],q[4];
u1(0.06249999999999997*pi) q[0];
cx q[3],q[4];
u2(0.0*pi,1.0*pi) q[4];
cx q[0],q[4];
u1(1.9375*pi) q[4];
cx q[0],q[4];
cx q[0],q[2];
u1(0.06249999999999997*pi) q[4];
u1(1.9375*pi) q[2];
u2(0.0*pi,1.0*pi) q[4];
u2(0.0*pi,1.0*pi) q[4];
cx q[2],q[4];
u1(0.06249999999999997*pi) q[4];
cx q[2],q[4];
cx q[0],q[2];
u1(1.9375*pi) q[4];
u1(0.06249999999999997*pi) q[2];
u2(0.0*pi,1.0*pi) q[4];
u2(0.0*pi,1.0*pi) q[4];
cx q[2],q[4];
u1(1.9375*pi) q[4];
cx q[2],q[4];
cx q[2],q[3];
u1(0.06249999999999997*pi) q[4];
u1(1.9375*pi) q[3];
u2(0.0*pi,1.0*pi) q[4];
u2(0.0*pi,1.0*pi) q[4];
cx q[3],q[4];
u1(0.06249999999999997*pi) q[4];
cx q[3],q[4];
cx q[0],q[3];
u1(1.9375*pi) q[4];
u1(0.06249999999999997*pi) q[3];
u2(0.0*pi,1.0*pi) q[4];
u2(0.0*pi,1.0*pi) q[4];
cx q[3],q[4];
u1(1.9375*pi) q[4];
cx q[3],q[4];
cx q[2],q[3];
u1(0.06249999999999997*pi) q[4];
u1(1.9375*pi) q[3];
u2(0.0*pi,1.0*pi) q[4];
u2(0.0*pi,1.0*pi) q[4];
cx q[3],q[4];
u1(0.06249999999999997*pi) q[4];
cx q[3],q[4];
cx q[0],q[3];
u1(1.9375*pi) q[4];
u2(0.0*pi,1.0*pi) q[0];
u1(0.06249999999999997*pi) q[3];
u2(0.0*pi,1.0*pi) q[4];
cx q[1],q[0];
u2(0.0*pi,1.0*pi) q[4];
u1(1.9375*pi) q[0];
cx q[3],q[4];
cx q[1],q[0];
u1(1.9375*pi) q[4];
u1(0.06249999999999997*pi) q[0];
cx q[1],q[2];
cx q[3],q[4];
u2(0.0*pi,1.0*pi) q[0];
u1(1.9375*pi) q[2];
u1(0.06249999999999997*pi) q[4];
u2(0.0*pi,1.0*pi) q[0];
u2(0.0*pi,1.0*pi) q[4];
cx q[2],q[0];
u3(0.0*pi,0.0*pi,0.25*pi) q[4];
u1(0.06249999999999997*pi) q[0];
cx q[2],q[0];
u1(1.9375*pi) q[0];
cx q[1],q[2];
u2(0.0*pi,1.0*pi) q[0];
u1(0.06249999999999997*pi) q[2];
u2(0.0*pi,1.0*pi) q[0];
cx q[2],q[0];
u1(1.9375*pi) q[0];
cx q[2],q[0];
u1(0.06249999999999997*pi) q[0];
cx q[2],q[3];
u2(0.0*pi,1.0*pi) q[0];
u1(1.9375*pi) q[3];
u2(0.0*pi,1.0*pi) q[0];
cx q[3],q[0];
u1(0.06249999999999997*pi) q[0];
cx q[3],q[0];
u1(1.9375*pi) q[0];
cx q[1],q[3];
u2(0.0*pi,1.0*pi) q[0];
u1(0.06249999999999997*pi) q[3];
u2(0.0*pi,1.0*pi) q[0];
cx q[3],q[0];
u1(1.9375*pi) q[0];
cx q[3],q[0];
u1(0.06249999999999997*pi) q[0];
cx q[2],q[3];
u2(0.0*pi,1.0*pi) q[0];
u1(1.9375*pi) q[3];
u2(0.0*pi,1.0*pi) q[0];
cx q[3],q[0];
u1(0.06249999999999997*pi) q[0];
cx q[3],q[0];
u1(1.9375*pi) q[0];
cx q[1],q[3];
u2(0.0*pi,1.0*pi) q[0];
u1(0.06249999999999997*pi) q[3];
u2(0.0*pi,1.0*pi) q[0];
cx q[3],q[0];
u1(1.9375*pi) q[0];
cx q[3],q[0];
u1(0.06249999999999997*pi) q[0];
u2(0.0*pi,1.0*pi) q[0];
