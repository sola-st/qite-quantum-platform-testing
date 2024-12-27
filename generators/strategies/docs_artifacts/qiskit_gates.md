API Reference
Standard gates
These operations are reversible unitary gates and they all subclass Gate. As a consequence, they all have the methods to_matrix(), power(), and control(), which we can generally only apply to unitary operations.

For example:


from qiskit.circuit.library import XGate
gate = XGate()
print(gate.to_matrix())             # X gate
print(gate.power(1/2).to_matrix())  # √X gate
print(gate.control(1).to_matrix())  # CX (controlled X) gate

[[0.+0.j 1.+0.j]
 [1.+0.j 0.+0.j]]
[[0.5+0.5j 0.5-0.5j]
 [0.5-0.5j 0.5+0.5j]]
[[1.+0.j 0.+0.j 0.+0.j 0.+0.j]
 [0.+0.j 0.+0.j 0.+0.j 1.+0.j]
 [0.+0.j 0.+0.j 1.+0.j 0.+0.j]
 [0.+0.j 1.+0.j 0.+0.j 0.+0.j]]
C3XGate(*args[, _force_mutable])	The X gate controlled on 3 qubits.
C3SXGate(*args[, _force_mutable])	The 3-qubit controlled sqrt-X gate.
C4XGate(*args[, _force_mutable])	The 4-qubit controlled X gate.
CCXGate(*args[, _force_mutable])	CCX gate, also known as Toffoli gate.
DCXGate(*args[, _force_mutable])	Double-CNOT gate.
CHGate(*args[, _force_mutable])	Controlled-Hadamard gate.
CPhaseGate(theta[, label, ctrl_state, ...])	Controlled-Phase gate.
CRXGate(theta[, label, ctrl_state, ...])	Controlled-RX gate.
CRYGate(theta[, label, ctrl_state, ...])	Controlled-RY gate.
CRZGate(theta[, label, ctrl_state, ...])	Controlled-RZ gate.
CSGate(*args[, _force_mutable])	Controlled-S gate.
CSdgGate(*args[, _force_mutable])	Controlled-S^dagger gate.
CSwapGate(*args[, _force_mutable])	Controlled-SWAP gate, also known as the Fredkin gate.
CSXGate(*args[, _force_mutable])	Controlled-√X gate.
CUGate(theta, phi, lam, gamma[, label, ...])	Controlled-U gate (4-parameter two-qubit gate).
CU1Gate(theta[, label, ctrl_state, ...])	Controlled-U1 gate.
CU3Gate(theta, phi, lam[, label, ...])	Controlled-U3 gate (3-parameter two-qubit gate).
CXGate(*args[, _force_mutable])	Controlled-X gate.
CYGate(*args[, _force_mutable])	Controlled-Y gate.
CZGate(*args[, _force_mutable])	Controlled-Z gate.
CCZGate(*args[, _force_mutable])	CCZ gate.
ECRGate(*args[, _force_mutable])	An echoed cross-resonance gate.
HGate(*args[, _force_mutable])	Single-qubit Hadamard gate.
IGate(*args[, _force_mutable])	Identity gate.
MSGate(num_qubits, theta[, label])	The Mølmer–Sørensen gate.
PhaseGate(theta[, label, duration, unit])	Single-qubit rotation about the Z axis.
RCCXGate(*args[, _force_mutable])	The simplified Toffoli gate, also referred to as Margolus gate.
RC3XGate(*args[, _force_mutable])	The simplified 3-controlled Toffoli gate.
RGate(theta, phi[, label, duration, unit])	Rotation θ around the cos(φ)x + sin(φ)y axis.
RXGate(theta[, label, duration, unit])	Single-qubit rotation about the X axis.
RXXGate(theta[, label, duration, unit])	A parametric 2-qubit
X
⊗
X
X⊗X interaction (rotation about XX).
RYGate(theta[, label, duration, unit])	Single-qubit rotation about the Y axis.
RYYGate(theta[, label, duration, unit])	A parametric 2-qubit
Y
⊗
Y
Y⊗Y interaction (rotation about YY).
RZGate(phi[, label, duration, unit])	Single-qubit rotation about the Z axis.
RZZGate(theta[, label, duration, unit])	A parametric 2-qubit
Z
⊗
Z
Z⊗Z interaction (rotation about ZZ).
RZXGate(theta[, label, duration, unit])	A parametric 2-qubit
Z
⊗
X
Z⊗X interaction (rotation about ZX).
XXMinusYYGate(theta[, beta, label, ...])	XX-YY interaction gate.
XXPlusYYGate(theta[, beta, label, duration, ...])	XX+YY interaction gate.
SGate(*args[, _force_mutable])	Single qubit S gate (Z**0.5).
SdgGate(*args[, _force_mutable])	Single qubit S-adjoint gate (~Z**0.5).
SwapGate(*args[, _force_mutable])	The SWAP gate.
iSwapGate(*args[, _force_mutable])	iSWAP gate.
SXGate(*args[, _force_mutable])	The single-qubit Sqrt(X) gate (
X
X
​
 ).
SXdgGate(*args[, _force_mutable])	The inverse single-qubit Sqrt(X) gate.
TGate(*args[, _force_mutable])	Single qubit T gate (Z**0.25).
TdgGate(*args[, _force_mutable])	Single qubit T-adjoint gate (~Z**0.25).
UGate(theta, phi, lam[, label, duration, unit])	Generic single-qubit rotation gate with 3 Euler angles.
U1Gate(theta[, label, duration, unit])	Single-qubit rotation about the Z axis.
U2Gate(phi, lam[, label, duration, unit])	Single-qubit rotation about the X+Z axis.
U3Gate(theta, phi, lam[, label, duration, unit])	Generic single-qubit rotation gate with 3 Euler angles.
XGate(*args[, _force_mutable])	The single-qubit Pauli-X gate (
σ
x
σ
x
​
 ).
YGate(*args[, _force_mutable])	The single-qubit Pauli-Y gate (
σ
y
σ
y
​
 ).
ZGate(*args[, _force_mutable])	The single-qubit Pauli-Z gate (
σ
z
σ
z
​
 ).
GlobalPhaseGate(phase[, label, duration, unit])	The global phase gate (
e
i
θ
e
iθ
 ).