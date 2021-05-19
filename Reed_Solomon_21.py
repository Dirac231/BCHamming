from qiskit import *
from matplotlib import *
from math import pi
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors import pauli_error, depolarizing_error
from qiskit.providers.aer import AerSimulator

initial_state = [0,1,1]

#QTF IMPLEMENTATION

def swap_registers(circuit, n):
    for qubit in range(n//2):
        circuit.swap(qubit, n-qubit-1)
    return circuit

def qft_rotations(circuit, n):
    if n == 0:
        return circuit
    n -= 1 
    circuit.h(n)
    for qubit in range(n): 
        circuit.cp(pi/2**(n-qubit), qubit, n)

def qft(circuit, n):
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit
    
def inverse_qft(circuit, n):
    qft_circ = qft(QuantumCircuit(n), n)
    invqft_circ = qft_circ.inverse()
    circuit.append(invqft_circ, circuit.qubits[:n])
    return circuit

#ENCODING: takes a message and return the circuit that encodes it

def encoder_RS(initial_state):
    qc = QuantumCircuit(39,3)
    for i in range(0,3):
        qc.initialize(initial_state[i], i) 
    for i in range(12,21):
        qc.h(i)
    inverse_qft(qc, 21)
    return qc

#DECODING takes the encoding circuit and returns the decoding one

def decoder_RS(aux):
    aux = qft(aux, 21)
    for i in range(2,12):
        aux.cx(i, i+19)
    for i in range(11, 20):
        aux.h(i)
    for i in range(11,20):
        aux.cx(i, i+19)
    for i in range(11, 20):
        aux.h(i)
    aux = inverse_qft(aux, 21)
    return aux

qc = decoder_RS(encoder_RS(initial_state))
qc.draw(output='mpl', scale=0.5)

#TESTING THE EXTENDED STABILIZER METHOD
extended_stabilizer_simulator = AerSimulator(method='extended_stabilizer')
tqc = transpile(qc, extended_stabilizer_simulator)
results = extended_stabilizer_simulator.run(tqc, shots=1).result()
counts = results.get_counts(0)
print('This succeeded?: {}'.format(results.success))


