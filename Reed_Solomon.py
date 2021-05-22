from qiskit import *
import unireedsolomon as rs
from matplotlib import *
from math import pi, floor
import numpy as np
from qiskit.providers.aer import AerSimulator

#PARAMETERS SETUP

#Parameters of the classical code used to generate the optimal quantum code.
#The code is built so that everything is a function of k_cl, the order of the finite field.

k_cl = int(input("Lenght of message: "))#Order of the finite field in terms of powers of 2
delta = floor((2**k_cl-1)/2+2) #Classical optimal minimum distance of the code
K = (2**k_cl) - delta #Number of classical bits sent
coder_cl = rs.RSCoder(2**k_cl -1, K)
SENT = k_cl*(2**k_cl - 1 - 2*K)
#Construction of the Quantum parameters, ENC = Total encoding Qbits needed, SENT = Sent Qbits
ENC = k_cl*(2**k_cl - 1)

print("-------------------------------------------")
print("Encoding Qbits: ", ENC)
print("Sent Qbits: ", k_cl)
print("Optimal distance: ", delta)
print("Maximum error-correcting: ", floor((K)/2), "/Symbol")
print("Order of the finite field: ", 2**k_cl)
print("-------------------------------------------")

#--------------------------------------------------------------------------------------

#LOAD THE MESSAGE FROM A FILE

initial_state = np.loadtxt('states.txt')
if (len(initial_state) != k_cl):
    print("Error: different number of states in the file (", len(initial_state), "VS", k_cl, ")")


#--------------------------------------------------------------------------------------

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

#------------------------------------------------------------------------------------

#ENCODING: takes a message and return the circuit that encodes it

def encoder_RS(initial_state):
    qc = QuantumCircuit(ENC + 2*k_cl*K)
    for i in range(0,k_cl):
        qc.initialize(initial_state[i], i) 
    for i in range(k_cl*(K + 1), ENC-k_cl*K):
        qc.initialize(initial_state[i], i)
    for i in range(ENC - k_cl*K,ENC):
        qc.h(i)
    inverse_qft(qc, ENC)
    return qc
       
#------------------------------------------------------------------------------------

#DECODING takes the encoding circuit and returns the decoding one

def decoder_RS(aux):
    aux = qft(aux, ENC)
    for i in range(k_cl+1,k_cl*(K+1)+1):
        aux.cx(i-1, i+ENC-k_cl-1)
    for i in range(ENC -k_cl*K, ENC):
        aux.h(i)
    for i in range(ENC-k_cl*K-1,ENC-1):
        aux.cx(i+1, i+ENC-k_cl+1)
    for i in range(ENC -k_cl*K-1, ENC-1):
        aux.h(i+1)
    aux = inverse_qft(aux, ENC)
    return aux

#------------------------------------------------------------------------------------
    
circ = decoder_RS(encoder_RS(initial_state))

cr = ClassicalRegister(2*k_cl*K, 'classic')
circ.add_register(cr)
for i in range(0, 2*k_cl*K):
    circ.measure(ENC+i,cr[i])
    
result = execute(circ, Aer.get_backend('aer_simulator_matrix_product_state')).result()
print('This succeeded?: {}'.format(result.success))
