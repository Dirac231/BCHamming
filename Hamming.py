import numpy as np 

from warnings import warn

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister


def num_to_binary(n, N):
    """Returns the binary representation of n

    Args:
        n (int): The number to be represented in binary
        N (int): The number of digits of the rapresentation

    Returns:
        bool: The binary representation of n

    es: num_to_binary(5,4) = 0101
    """
    Nbits=2**N
    if n>=Nbits: return 0
    return bin(n+2*Nbits)[4:]


def is_power_2(n):
    """Returns True if the number is a power of two"""
    return n & (n-1) == 0


def HammingCircuit(N, name="Hamming", ancillas=1):
    """Constructs a circuit with the qubits named in Hamming fashion"""
    registers = []
    for i in range(2**N):
        prefix = "p" if is_power_2(i) else "d"
        registers.append(QuantumRegister(1, prefix+num_to_binary(i, N)))
    if ancillas>0:
        registers.append(QuantumRegister(N*ancillas,'anc'))
    circuit=QuantumCircuit(*registers) #circuit already with ancillas
    circuit.N=N
    return circuit

def swapper(N):
    """
    Circuit that shifts the every qubit right by the number of
    power-of-two qubits before it
    """
    qc = HammingCircuit(N, name="Swapper", ancillas=0)
    source = 2**N - N - 2
    target = 2**N - 1
    while source >= 0:
        if is_power_2(target):
            target -= 1
        qc.swap(source, target)
        source -= 1
        target -= 1
    

    return qc.to_gate(label="Swapper")


def encoder(N):
    """Encoder for the quantum hamming code"""

    qc = HammingCircuit(N, name="Encoder", ancillas=0)

    for p in range(N):
        p = 2**p
        [qc.cx(i, p) for i in range(2**N) if (i & p) == p and i != p]


    return qc.to_gate(label="Encoder")


def hamming_encode(N):
    """Returns a hamming encoding circuit"""
    qc = HammingCircuit(N, ancillas=0)
    qc.append(swapper(N), [*range(2**N)])
    qc.append(encoder(N), [*range(2**N)])
    
    qc.draw()
    return qc.to_gate(label="Hamming encode")


def bit_phase_encoder(N, name="bit phase encoder"):
    prova = QuantumCircuit(2**N)
    prova.append(hamming_encode(N), list(range(2**N)))

    prova.h(list(range(2**N - N - 1)))

    prova.append(hamming_encode(N), list(range(2**N)))
    return prova.to_gate(label=name)

def xor(N):
    #This is the gate that calculates the xor of all the position with ones, this gives the position of the faulty qbit
    circ=HammingCircuit(N)
    nqubits=2**N
    for i in range(1,nqubits):
        for j in range(0,N):
            if i & 2**j == 2**j: circ.cx(i,nqubits+j)
    return circ.to_gate(label='Initialize')

def correct(N):
    #This is the gate that corrects the faulty qbit
    circ=HammingCircuit(N)
    nqubits=2**N
    count=np.zeros(N)
    for i in range(1,nqubits):
        count=count+1
        for j in range(N):
            count[j]=count[j]%(2**j)
            if count[j]==0 and i!=1: circ.x(nqubits+j)
            if i==1 and j!=0: circ.x(nqubits+j)
        circ.mct([*range(nqubits,nqubits+N)],i)
    return circ.to_gate(label='Correction')

def HammingGate0(N):
    #Hamming Gate resistant to bit-fips
    circ=HammingCircuit(N)
    circ.append(xor(N),[*range(2**N+N)])
    circ.append(correct(N),[*range(2**N+N)])
    return circ.to_gate(label='Hamming0')

def HammingRedundant(n):
    #Takes a integer "n" and makes the binary representation of that integer hamming redundant
    bits=int(np.log2(n))+1
    parity=int(np.log2(bits))+2
    total=2**(parity-1)
    N,j=0,0
    #shift the digits in the correct positions for the hamming code
    for i in range(total):
        if i!=0 and int(np.log2(i))!=np.log2(i):
            N=N+(n&(2**j)==2**j)*(2**i)
            j=j+1
    #puts the parity bit in place except for the global parity bit
    for i in range(parity):
        i=2**i
        for j in range(i,total):
            N=N^((2**i)*((j&i==i)&((N&2**j)!=0)))
    #Global parity bit (yet to be tested)
    #for i in range(1,total):N=N^((N&2**i)==1)
    return N

def classic_input(n,N=None):
    #n is the number in integer format, N is the size of the gate
    #doesn't work and i 
    if N==None: N=int(np.log2(n))+1
    if (n>=2**N): raise 'ma sei trimò'
    registers=QuantumRegister(N)
    circuit=QuantumCircuit(registers)
    for i in range(N):
        j=2**i
        if (n&j)==j: circuit.x(i)
    return circuit.to_gate(num_to_binary(n,N))