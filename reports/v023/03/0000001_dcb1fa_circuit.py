qr = QuantumRegister(11, name='qr')
cr = ClassicalRegister(11, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
# TIMESTAMP: 1738243210.791898

# Apply gate operations
# <START_GATES>
qc.z(qr[9])
qc.rx(4.695018, qr[6])
qc.s(qr[7])
qc.cry(2.828155, qr[9], qr[5])
qc.t(qr[2])
# <END_GATES>

# Section: Measurement
qc.measure(qr, cr)