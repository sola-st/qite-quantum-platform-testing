grammar Qiskit;

program: importStatements circuitDeclaration circuitBody execution;

importStatements:
    'from' 'qiskit' 'import' 'QuantumCircuit,' 'Aer,' 'transpile,' 'assemble,' 'execute';

circuitDeclaration:
    'qc' '=' 'QuantumCircuit' '(' number ',' number ')'
    # Example: QuantumCircuit(3, 3);

circuitBody:
    gateInstruction* measurement*;

gateInstruction:
    'qc' '.' gateName '(' qubitList ')' comment?;

measurement:
    'qc' '.' 'measure' '(' qubit ',' classicalBit ')' comment?;

execution:
    backendDeclaration shotsDeclaration jobExecution resultHandling;

backendDeclaration:
    'backend' '=' 'Aer.get_backend' '(' "'qasm_simulator'" ')'
    # Example: backend = Aer.get_backend('qasm_simulator');

shotsDeclaration:
    'shots' '=' number
    # Example: shots = 1024;

jobExecution:
    'job' '=' 'execute' '(' 'qc' ',' 'backend' ',' 'shots' '=' number ')'
    # Example: job = execute(qc, backend, shots=1024);

resultHandling:
    'result' '=' 'job.result' '()'
    'counts' '=' 'result.get_counts' '(' 'qc' ')'
    'print' '(' 'counts' ')';

gateName:
    'h'
    | 'cx'
    | 'x';

qubitList:
    qubit (',' qubit)?;

qubit:
    'q[' number ']'
    | number;

classicalBit:
    'c[' number ']'
    | number;

number:
    DIGIT+;

comment:
    '#' ~[\r\n]*;

DIGIT:
    [0-9];
