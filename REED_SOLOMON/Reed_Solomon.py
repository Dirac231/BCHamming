from qiskit import *
from unireedsolomon import *
from matplotlib import *
from math import pi, floor
import numpy as np
from numpy.polynomial import Polynomial
from qiskit.providers.aer import AerSimulator
from qiskit.circuit.library import QFT


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

#LOADS THE MESSAGE FROM A FILE

initial_state = np.loadtxt('states.txt')
if (len(initial_state) != k_cl):
    print("Error: different number of states in the file (", len(initial_state), "VS", k_cl, ")")

#--------------------------------------------------------------------------------------

#QTF IMPLEMENTATION

fourier = QFT(num_qubits=ENC, approximation_degree=appr, do_swaps=True, inverse=False, insert_barriers=True, name='qft')
inv_fourier = QFT(num_qubits=ENC, approximation_degree=appr, do_swaps=True, inverse=True, insert_barriers=True, name='qft-1')

#-----------------------------------------------------------------------------------

#SIMULATES THE CIRCUIT

def simulate(circ):
    """Simulate the circuit with matrix product state and return the list of results"""
    result = execute(circ, Aer.get_backend('aer_simulator_matrix_product_state'), shots=100).result()
    print('Simulation Success: {}'.format(result.success))
    print("Time taken: {} sec".format(result.time_taken))
    counts = result.get_counts(0)
    return counts

#------------------------------------------------------------------------------------

#MEASURE FUNCTIONS

def measure_encoding(circ):
    """Measure the Qbits used in the encoding, i.e. if the lenght is 3, the first 21 Qbits"""
    cr = ClassicalRegister(ENC, 'encoded')
    circ.add_register(cr)
    for i in range(0, ENC):
        circ.measure(i,cr[i])
    results = simulate(circ)
    encoded = max(results, key=results.get)
    return encoded

def get_qbits(circ):
    """Measure the Qbits with the message, i.e. if the lenght is 3, the first 3 Qbits"""
    cr = ClassicalRegister(k_cl, 'out')
    circ.add_register(cr)
    for i in range(0,k_cl):
        circ.measure(i, cr[i]) 
    for i in range(k_cl*(K + 1), ENC-k_cl*K):
        circ.measure(i, cr[i])
    results = simulate(circ)
    qbits = max(results, key=results.get)
    return qbits

def get_syndrome(circ):
    """Measure the Qbits with the syndrome, i.e. if the lenght is 3, the last 18 Qbits"""
    cr = ClassicalRegister(2*k_cl*K)
    circ.add_register(cr)
    for i in range(0, 2*k_cl*K):
        circ.measure(ENC+i,cr[i])
    #orders the syndromes in descending order in term of the occurrences
    ordered_res = {k: v for k, v in sorted(simulate(circ).items(), key=lambda item: item[1])}   
    syndromes = list(ordered_res)[::-1]
    return syndromes

#------------------------------------------------------------------------------------

#GIVEN THE CLASSICAL SYNDROME, RETURNS THE POSITIONS OF THE ERRORS USING CLASSICAL BERLEKAMP-MASSEY

def error_string(classical_syn):
    k1 = int(ENC/k_cl)
    k2 = int(((ENC-K*k_cl)/k_cl))
    prime = int(hex(find_prime_polynomials(c_exp=k_cl,single=True)),16)
    coder = rs.RSCoder(k1, k2, prim=prime,c_exp=k_cl)
    error_bf, sigma_bf = coder._berlekamp_massey_fast(coder._list2gfpoly(str(classical_syn)))
    eval_tmp_bf, bf = coder._chien_search_faster(error_bf)
    Y = coder._forney(sigma_bf, eval_tmp_bf)
    Elist = []
    if(classical_syn != "000"):

        if len(Y) >= len(bf): 
            for i in range(coder.gf2_charac):
                if i in bf:
                    Elist.append(Y[bf.index(i)])
            E = Polynomial( Elist[::-1])
            error_bits = [bin(int(i))[2:] for i in Elist]
            s = ""
            for i in range(len(error_bits)):                
                s += error_bits[i]
            s = s[::-1]
        return s
    else:
        return ""
    
    
def error_locator(syn):
    """take the syndrome computed by the quantum circuit and apply error_string"""
    for x in syn:  
        BFsyndrome = oct(int((x)[:k_cl*K],2))[2:]         #bit flip syndrome string
        PFsyndrome = oct(int((x)[k_cl*K:],2))[2:]         #phase flip syndrome string
        #Since the QFT has a degree of approximation, it can change the syndrome to a wrong one. 
        #We know for sure that if this error is raised the syndrome was modified by the QFT, so in this case we try to use the next syndrome with most occurrences.                                                
        try:                                              #use functions in unireedsolomon to compute the error locations bf, pf
            bf = error_string(BFsyndrome)
            pf = error_string(PFsyndrome)
            return bf,pf
        except RSCodecError:
            continue

#------------------------------------------------------------------------------------

"""ENCODING: takes a message and return the circuit that encodes it"""

def encoder(initial_state):
    """Takes a message and return the circuit that encodes it"""
    qc = QuantumCircuit(encode_reg)
    for i in range(0,k_cl):
        qc.initialize(initial_state[i], i) 
    for i in range(k_cl*(K + 1), ENC-k_cl*K):
        qc.initialize(initial_state[i], i)
    for i in range(ENC - k_cl*K,ENC):
        qc.h(i)
    qc.append(inv_fourier, encode_reg[:ENC])
    return qc


#CIRCUIT TO COMPUTE THE SYNDROME

def syn_circuit(qc):
    """Takes the ecoding circuit and computes the syndrome"""
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


#CORRECTS THE ERRORS AND RETURNS THE ORIGINAL MESSAGE

def decoder(circ):
    """Takes the circuits that computes the syndrome (given by syn_circuite) and returns the original message"""
    syn = get_syndrome(circ)
    bf,pf = error_locator(syn)
    if(bf != "1" or syn != "0"*k_cl*K*2):
        for i in range(len(bf)):
            if (bf[i] == 1):
                circ.x(i)
    if (pf != "1" or syn != "0"*k_cl*K*2):
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

def send_message(initial_state):
    """Does everything, given the inital_state"""
    qc = encoder(initial_state)

    #INSERT ERRORS HERE: (such as qc.x(4) or z-errors)

    qc = syn_circuit(qc)
    retrieved = decoder(qc)
    print("Retrieved message: ", retrieved[:3][::-1])
    print("Compared with: ")
    for i in initial_state:
        print(i,"\n")
    print("Syndrome was: ", retrieved[3:][::-1])

#------------------------------------------------------------------------------------

#Calls the function that does everything
send_message(initial_state)
