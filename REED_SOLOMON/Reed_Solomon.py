from qiskit import *
#import unireedsolomon as rs
from matplotlib import *
from math import pi, floor
import numpy as np
from qiskit.providers.aer import AerSimulator
from qiskit.circuit.library import QFT
from Berlekamp_Massey import *

#PARAMETERS SETUP

#Parameters of the classical code used to generate the optimal quantum code.
#The code is built so that everything is a function of k_cl, the order of the finite field.

k_cl = int(input("Lenght of message: "))        #Order of the finite field in terms of powers of 2
appr = int(input("QFT approximation degree (the lower the better): ")) 
delta = floor((2**k_cl-1)/2+2)                  #Classical optimal minimum distance of the code
K = (2**k_cl) - delta                           #Number of classical bits sent
ENC = k_cl*(2**k_cl - 1)                        #Total encoding Qbits needed
encode_reg = QuantumRegister(ENC+2*k_cl*K)

print("-------------------------------------------")
print("Encoding Qbits: ", ENC)
print("Sent Qbits: ", k_cl)
print("Optimal distance: ", delta)
print("Maximum error-correcting: ", floor((K)/2), "/Symbol")
print("-------------------------------------------")


#--------------------------------------------------------------------------------------

#LOAD THE MESSAGE FROM A FILE

initial_state = np.loadtxt('states.txt')
if (len(initial_state) != k_cl):
    print("Error: different number of states in the file (", len(initial_state), "VS", k_cl, ")")

#--------------------------------------------------------------------------------------

#QTF IMPLEMENTATION

fourier = QFT(num_qubits=ENC, approximation_degree=appr, do_swaps=True, inverse=False, insert_barriers=True, name='qft')
inv_fourier = QFT(num_qubits=ENC, approximation_degree=appr, do_swaps=True, inverse=True, insert_barriers=True, name='qft-1')


#-----------------------------------------------------------------------------------

#MEASURE FUNCTIONS

def measure_encoding(circ):
    cr = ClassicalRegister(ENC, 'encoded')
    circ.add_register(cr)
    for i in range(0, ENC):
        circ.measure(i,cr[i])
    return circ

def get_qbits(circ):
    cr = ClassicalRegister(k_cl, 'out')
    circ.add_register(cr)
    for i in range(0,k_cl):
        circ.measure(i, cr[i]) 
    for i in range(k_cl*(K + 1), ENC-k_cl*K):
        circ.measure(i, cr[i])
    results = list(simulate(circ))
    return results


#------------------------------------------------------------------------------------

#ENCODING: takes a message and return the circuit that encodes it

def encoder_RS(initial_state):
    qc = QuantumCircuit(encode_reg)
    for i in range(0,k_cl):
        qc.initialize(initial_state[i], i) 
    for i in range(k_cl*(K + 1), ENC-k_cl*K):
        qc.initialize(initial_state[i], i)
    for i in range(ENC - k_cl*K,ENC):
        qc.h(i)
    qc.append(inv_fourier, encode_reg[:ENC])
    qc.x(0)
    qc.z(2)
    return qc

def decoder_RS(qc):
    qc.append(fourier, encode_reg[:ENC])
    for i in range(k_cl+1,k_cl*(K+1)+1):
        qc.cx(i-1, i+ENC-k_cl-1)
    for i in range(ENC -k_cl*K, ENC):
        qc.h(i)
    for i in range(ENC-k_cl*K-1,ENC-1):
        qc.cx(i+1, i+ENC-k_cl+1)
    for i in range(ENC -k_cl*K-1, ENC-1):
        qc.h(i+1)
    qc.append(inv_fourier, encode_reg[:ENC])
    return qc

def get_syndrome(circ):
    cr = ClassicalRegister(2*k_cl*K)
    circ.add_register(cr)
    for i in range(0, 2*k_cl*K):
        circ.measure(ENC+i,cr[i])
    results = simulate(circ)
    syn = max(results, key=results.get)
    return syn

def error_locator(syn):          

    BFsyndrome = (syn)[:k_cl*K]         #bit flip syndrome string
    PFsyndrome = (syn)[k_cl*K:]         #phase flip syndrome string


    print("-------------------------------------------")
    print("Bit fip Syndrome: ", BFsyndrome)
    print("Phase flip Syndrome: ", PFsyndrome)
    
    #Given the syndrome return the error locator polynomial
    bf = berlekamp_massey(BFsyndrome)
    pf = berlekamp_massey(PFsyndrome)
    
    print("Error Locator Bit-flip: ", bf)
    print("Error Locator Phase-flip: ", pf)

    return (bf,pf)


def recovery(circ, bf, pf):
    for i in range(len(bf)):
        if (bf[i] == 1):
            circ.x(i)
    if (pf != []):
        for i in range(ENC):
            circ.h(i)
        for i in range(len(pf)):
            if (pf[i] == 1):
                circ.z(i)
        for i in range(ENC):
            circ.h(i)
    circ.append(fourier, encode_reg[:ENC])
    message = get_qbits(circ)
    return message
#------------------------------------------------------------------------------------

#SIMULATE THE CIRCUIT

def simulate(circ):
    #simulator
    result = execute(circ, Aer.get_backend('aer_simulator_matrix_product_state'), shots=10).result()
    print('Simulation Success: {}'.format(result.success))
    print("Time taken: {} sec".format(result.time_taken))
    counts = result.get_counts(0)
    return counts

#------------------------------------------------------------------------------------

qc = decoder_RS(encoder_RS(initial_state))
message = recovery(qc, [1,0,0], [0,0,1])
print(message)
qc.draw(output='mpl', filename='fig.png')
print("Finished")
