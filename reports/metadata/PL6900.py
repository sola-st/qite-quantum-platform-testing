qr = QuantumRegister(11, name='qr')
cr = ClassicalRegister(11, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
# TIMESTAMP: 1738167512.468567

# Apply gate operations
# <START_GATES>
qc.mcrz(2.823119, [qr[1], qr[6], qr[3]], qr[10])
qc.cswap(qr[3], qr[8], qr[6])
qc.sx(qr[1])
qc.ccx(qr[7], qr[9], qr[2])
qc.rxx(0.688059, qr[4], qr[2])
# <END_GATES>

# Section: Measurement
qc.measure(qr, cr)