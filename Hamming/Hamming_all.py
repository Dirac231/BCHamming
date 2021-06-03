import numpy as np 
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


def HammingCircuit(N, classical_registers=False, name=None, ancillas=None):
    """It gives you a circuit with 2^N qbits of (message + redundancy)

    Args:
        N (int): Order of the Hamming cirucit
        classical_registers (Bool, int): If True if gives an amount of classical registers equal to the number of qbits, if you want a specific number of classical registers just write the number you want. Defaults to False.
        name (str): Name of the circuit. Defaults to None.
        ancillas (int): Is the number of ancillas of the circuit. Defaults to zero.

    Returns:
        circuit: Returns a circuit with just the qbits labeled as the parity and signal
    """
    
    if ancillas is None: ancillas = 2*N-1
    registers=[]
    for i in range(2**N):
        prefix='s' #s stands for signal
        if is_power_2(i): prefix='p' #c stands for parity
        registers.append(QuantumRegister(1,prefix+num_to_binary(i, N)))
    if classical_registers!=False: 
        if classical_registers==True: registers.append(ClassicalRegister(2**N + ancillas))
        else: registers.append(ClassicalRegister(classical_registers))

    if ancillas > 0: registers.append(QuantumRegister(ancillas))
    circuit=QuantumCircuit(*registers) #circuit already with ancillas
    circuit.N=N
    if name is not None: circuit.name = name
    return circuit


def Swapper(N):
    """Circuit that shifts the every qubit right by the number of
    power-of-two qubits before it

    Args:
        N (int): Order of Hamming code

    Returns:
        gate: swapper
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


def ReverseSwapper(N):
    """
    Circuit that shifts the every qubit left by the number of
    power-of-two qubits before it
    """
    qc = HammingCircuit(N, ancillas=0)

    source = 0
    target = 0
    while target < 2**N:
        if is_power_2(target):
            target += 1
            continue
        qc.swap(source, target)
        source += 1
        target += 1

    return qc.to_gate(label="Reverse Swapper")


def Encoder(N):
    """Encoder for the quantum hamming code"""

    qc = HammingCircuit(N, name="Encoder", ancillas=0)

    for p in range(N):
        p = 2**p
        [qc.cx(i, p) for i in range(2**N) if (i & p) == p and i != p]


    return qc.to_gate(label="Encoder")


def Hamming_bit_encoder(N, kind="bit", name="bit encoder"):
    """Creates quantum Hamming bit encoder circuit of order N

    Args:
        N (int): Order of the circuit
        name (str, optional): Name of the circuit. Defaults to "bit encoder".
        kind (str, optional):  Set to "bit" for correcting bit flip errors,
        "phase" for correcting phase flip errors.

    Returns:
        Gates: Quantum Hamming bit encoder circuit of order N
    """
    qc = HammingCircuit(N, ancillas=0)
    qc.append(Swapper(N), [*range(2**N)])
    qc.append(Encoder(N), [*range(2**N)])
    if kind=="phase":
        qc.h([*range(2**N)])

    return qc.to_gate(label=name)



def is_valid_input(kind):
    """Helper function that checks if kind="bit", "phase" or "both" and raises
    an exeption if it isn't
    """
    if kind not in ["bit", "phase", "both"]:
        message = f"The kind argument must be one of bit, phase or both, received {kind} instead"
        raise Exception(message)
    return True




def HammingOrder(n):
    """Gives you the order of the Hamming gate as a function of n

    Args:
        n (int): lenght of the input message

    Returns:
        N (int): order of the Hamming gate
    """
    for i in range(0,15):
        N=2**i
        if N-i-1>=n: return i
            


def syndrome(N):
    """This gate calculates the syndrome, this gives the position of the faulty qbit"""
    circ=HammingCircuit(N, ancillas=N)
    nqubits=2**N
    for i in range(1,nqubits):
        for j in range(0,N):
            if i & 2**j == 2**j: circ.cx(i,nqubits+j)
    return circ.to_gate(label='syndrome')


def apply_syndrome(N):
    """This gate that corrects the faulty qbit identified in the syndrome"""
    circ=HammingCircuit(N, ancillas=N)
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


def Hamming_bit_decoder(N,kind='bit',read=True,name='decoder'):
    """Hamming Gate resistant to bit-fips"""
    circ=HammingCircuit(N, ancillas=N)
    if kind=='phase':
        circ.h([*range(2**N)])
    circ.append(syndrome(N),[*range(2**N+N)])
    circ.append(apply_syndrome(N),[*range(2**N+N)])
    if read==True: circ.append(ReverseSwapper(N), [*range(2**N)])
    return circ.to_gate(label=name)




# I don't know if these functions are still useful
def HammingRedundant(n):
    """Takes a integer "n" and makes the binary representation of that integer hamming redundant"""
    bits=int(np.log2(n))+1
    parity=int(np.log2(bits))+2
    total=2**(parity-1)
    N,j=0,0
    #shift the digits in the correct positions for the hamming code
    for i in range(total):
        if is_power_2(i) is False:
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