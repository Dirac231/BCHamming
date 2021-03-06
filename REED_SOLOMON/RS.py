from qiskit import *
from unireedsolomon import *
from matplotlib import *
from math import *
from collections import defaultdict
import numpy as np
from numpy.polynomial import Polynomial
from qiskit.providers.aer import AerSimulator
from qiskit.circuit.library import QFT
from qiskit.visualization import plot_histogram

#PARAMETERS SETUP

#Parameters of the classical code used to generate the optimal quantum code.
#The code is built so that everything is a function of k_cl, the order of the finite field.

#The initial state is read from the file states.txt

def init_decoder():
    global initial_state, k_cl, delta, K, ENC, encode_reg, ecc, shots, fourier, inv_fourier,provider
    provider = IBMQ.load_account()
    initial_state = np.loadtxt('states.txt')
    k_cl = len(initial_state)                       #Order of the finite field in terms of powers of 2, corresponds to the amount of qbits sent

    delta = floor((2**k_cl-1)/2+2)                  #Classical optimal minimum distance of the code
    K = (2**k_cl) - delta                           #Number of classical bits sent, directly related to the error-correcting capability of the code ecc = floor((K+1)/2) 
    ENC = k_cl*(2**k_cl - 1)                        #Total encoding Qbits needed
    encode_reg = QuantumRegister(ENC+2*k_cl*K)      #Quantum Register used to construct the full circuit
    ecc = floor((K+1)/2)                                #Maximum error correction capability per symbol
    shots = 128

    #Initialization of the parameters is completed
    print("")
    print("Reading from file: found ",k_cl," Qbits: \n")

    print("Parameters of the code: ")
    print("-------------------------------------------")
    print("Encoding Qbits: ", ENC)
    print("Sent Qbits: ", k_cl*(2**k_cl-1-2*K))
    print("Maximum error-correcting: ", ecc, "/Symbol = ", ecc*k_cl, "/Encoded Qbit")
    print("-------------------------------------------")

    #--------------------------------------------------------------------------------------

    #QTF IMPLEMENTATION

    #A quantum fourier transform is used both for encoding and decoding purposes

    fourier = QFT(num_qubits=ENC, approximation_degree=0, do_swaps=True, inverse=False, insert_barriers=False, name='qft')
    inv_fourier = QFT(num_qubits=ENC, approximation_degree=0, do_swaps=True, inverse=True, insert_barriers=False, name='qft-inverse')

#-----------------------------------------------------------------------------------

#SIMULATES THE CIRCUIT

def simulate(qc):
    """Simulates the circuit using the cloud-computing services of IBMq, this is always the recommended choice to run simulations"""
    provider = IBMQ.get_provider(hub='ibm-q')
    backend=provider.get_backend('simulator_mps')
    result = execute(qc, backend,shots=shots).result()
    print('Simulation Success: {}'.format(result.success))
    print("Time taken: {} sec".format(result.time_taken))
    counts = result.get_counts(0)
    return counts

#------------------------------------------------------------------------------------

#MEASURE FUNCTIONS

def measure_encoding(qc):
    """Measure the Qbits used in the encoding, i.e. if the lenght is 3, the first 21 Qbits"""
    cr = ClassicalRegister(ENC, 'encoded')
    qc.add_register(cr)
    for i in range(0, ENC):
        qc.measure(i,cr[i])
    results = simulate(qc)
    encoded = max(results, key=results.get)
    return encoded


def get_qbits(qc):
    """Measure the Qbits with the message, i.e. if the lenght is 3, the first 3 Qbits"""
    cr = ClassicalRegister(k_cl*(2**k_cl-1-2*K), 'out')
    qc.add_register(cr)
    for i in range(0,k_cl):
        qc.measure(i, cr[i]) 
    for i in range(k_cl*(K + 1), ENC-k_cl*K):
        qc.measure(i, cr[i])
    results = simulate(qc)
    qbits = max(results, key=results.get)
    return qbits,results


def get_syndrome(qc):
    """Measure the Qbits with the syndrome, i.e. if the lenght is 3, the last 18 Qbits"""
    cr = ClassicalRegister(2*k_cl*K)
    qc.add_register(cr)
    for i in range(0, 2*k_cl*K):
        qc.measure(ENC+i,cr[i])
    #orders the syndromes in descending order in term of the occurrences
    ordered_res = {k: v for k, v in sorted(simulate(qc).items(), key=lambda item: item[1])}  
    syndromes = list(ordered_res)[::-1]
    return syndromes

#------------------------------------------------------------------------------------

#GIVEN THE CLASSICAL SYNDROME, RETURNS THE POSITIONS OF THE ERRORS USING CLASSICAL BERLEKAMP-MASSEY

#Performs a Berlekamp-Massey algorithm in order to find the error locator polynomial relative to the syndrome#
def error_string(classical_syn):
    k1 = int(ENC/k_cl)
    k2 = int(((ENC-K*k_cl)/k_cl))
    prime = int(hex(find_prime_polynomials(c_exp=k_cl,single=True)),16)
    coder = rs.RSCoder(k1, k2, prim=prime,c_exp=k_cl)
    error_bf, sigma_bf = coder._berlekamp_massey_fast(coder._list2gfpoly(str(classical_syn)))
    eval_tmp_bf, bf = coder._chien_search_faster(error_bf)
    Y = coder._forney(sigma_bf, eval_tmp_bf)
    Elist = []
    if(classical_syn != "0"*k_cl):

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
        BFsyndrome = oct(int((x[::-1])[:k_cl*K],2))[2:]         #bit flip syndrome string
        PFsyndrome = oct(int((x[::-1])[k_cl*K:],2))[2:]         #phase flip syndrome string

        #Performs the error locator finding for each measured syndrome, if a error occurs, it computes the errors associated with the next most probable syndrome
        try:                                              #uses functions in the unireedsolomon library to compute the error locations bf, pf
            bf = error_string(BFsyndrome)
            pf = error_string(PFsyndrome)
            return bf,pf,x
        except (RSCodecError,ValueError):
            continue
    print("No valid syndrome was found, too many errors try increasing the number of shots.")
    exit()

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

def decoder(qc):
    """Takes the ecoding circuit, computes the syndrome and corrects the message"""
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
    syn = get_syndrome(qc)
    bf,pf,x = error_locator(syn)
    if(bf != "1" or x[:k_cl*K] != "0"*k_cl*K):
        for i in range(len(bf)):
            if (bf[i] == "1"):
                qc.x(i)
    if (pf != "1" or x[k_cl*K:] != "0"*k_cl*K):
        for i in range(ENC):
            qc.h(i)

        for i in range(len(pf)):
            if (pf[i] == "1"):
                qc.z(i)

        for i in range(ENC):
            qc.h(i)
    qc.append(fourier, encode_reg[:ENC])
    message,occurrences = get_qbits(qc)
    occurrences = zip([x[:3][::-1] for x in occurrences.keys()] , list(occurrences.values()))
    D = defaultdict(int)
    for k,v in occurrences:
        D[k]+= int(v)
    occurrences = dict(D)
    return qc,message,x,occurrences

#------------------------------------------------------------------------------------


def send_message(initial_state):
    """Auxiliary testing function, sends the message contained in the file states.txt and returns the simulation circuit."""
    qc = encoder(initial_state)                #Classical optimal minimum distance of the code
    #INSERT ERRORS HERE: (such as qc.x(4) or z-errors)
    qc,retrieved,syn,occurrences = decoder(qc)
    plot_histogram(occurrences, color='midnightblue', title="Message occurrences").savefig("histogram.png")
    print("Most probable message: ", retrieved[:3][::-1])
    print("Occurrences: ", occurrences)
    print("Compared with: ")
    for i in initial_state:
        print(i,"\n")
    print("Syndrome was: ", syn[::-1])
    qc.draw(output='mpl', filename='prova.png')
    return qc

#------------------------------------------------------------------------------------

