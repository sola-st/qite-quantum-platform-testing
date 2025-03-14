qr = QuantumRegister(11, name='qr')
cr = ClassicalRegister(11, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
# TIMESTAMP: 1737648418.0954087

# Apply gate operations
# <START_GATES>
qc.s(qr[8])
qc.cp(3.729997, qr[0], qr[5])
qc.dcx(qr[10], qr[0])
qc.dcx(qr[4], qr[6])
qc.swap(qr[0], qr[5])
# <END_GATES>

# Section: Measurement
qc.measure(qr, cr)