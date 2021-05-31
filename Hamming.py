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


def HammingCircuit(N, classical_registers=False, name=None, ancillas=None):
    """it gives you a circuit with 2^N qbits of (message + redundancy)

    Args:
        N (int): Order of the Hamming cirucit
        ClassicalRegisters (Bool, int): If True if gives an amount of classical registers equal to the number of qbits, if you want a specific number of classical registers just write the number you want. Defaults to False.
        name (str): Name of the circuit. Defaults to None.
        ancillas (int): Is the number of ancillas of the circuit. Defaults to zero.

    Returns:
        circuit: Returns a circuit with just the qbits labeled as the parity and signal
    """
    
    if ancillas is None: ancillas = 2*N-1
    registers=[]
    for i in range(2**N):
        prefix='s' #s stands for signal
        if i==0 or np.log2(i)==int(np.log2(i)): prefix='p' #c stands for parity
        registers.append(QuantumRegister(1,prefix+num_to_binary(i, N)))
    if classical_egisters!=False: 
        if classical_egisters==True: registers.append(ClassicalRegister(2**N + ancillas))
        else: registers.append(ClassicalRegister(classical_egisters))

    if ancillas > 0: registers.append(QuantumRegister(ancillas))
    circuit=QuantumCircuit(*registers) #circuit already with ancillas
    #circit=QuantumCircuit(*registers)
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


def Encoder(N):
    """Encoder for the quantum hamming code"""

    qc = HammingCircuit(N, name="Encoder", ancillas=0)

    for p in range(N):
        p = 2**p
        [qc.cx(i, p) for i in range(2**N) if (i & p) == p and i != p]


    return qc.to_gate(label="Encoder")


def Hamming_phase_encoder(N, name="phase encoder"):
    qc = HammingCircuit(N, ancillas=0)
    qc.append(Hamming_bit_encoder(N), list(range(2**N)))
    qc.h(list(range(2**N)))
    
    return qc.to_gate(label=name)


def Hamming_bit_encoder(N, name="bit encoder"):
    qc = HammingCircuit(N, ancillas=0)
    qc.append(Swapper(N), [*range(2**N)])
    qc.append(Encoder(N), [*range(2**N)])

    return qc.to_gate(label=name)


def is_valid_input(kind):
    if kind not in ["bit", "phase", "both"]:
        message = f"The kind argument must be one of bit, phase or both, received {kind} instead"
        raise Exception(message)
    return True


def Hamming_encode(N, kind="both", name="Hamming encoder"):
    """Returns a hamming encoding circuit

    Args:
        N (int): Order of the hamming code used, acts on 2^N qubits
        kind (str, optional): Set to "bit" for correcting bit flip errors,
        "phase" for correcting phase flip errors, "both" corrects both errors. 
        Defaults to "both".

    Returns:
        Gates: The gates composing the circuit
    """

    if not is_valid_input(kind):
        return

    if kind == "both": 
        qc = HammingCircuit(N+1, ancillas=0)

    if kind in ["bit", "both"]:
        qc.append(Hamming_bit_encoder(N), [*range(2**N)])
        N += 1
    if kind in ["phase", "both"]:
        qc.append(Hamming_phase_encoder(N), [*range(2**N)])
    
    return qc.to_gate(label=name)


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


def Hamming_decode(N, kind="both",read=True, name="Hamming decoder"):
    """It corrects the output, if you don't want to read the output just write read=False, that way
    the bits don't get switched

    Args:
        N (int): The order of the Hamming code
        kind (str): The kind argument must be one of bit, phase or both. Defaults to "both".
        read (bool): If True returns the output on the first qbits, otherwise it doesn't switch the output. Defaults to True.
        name (str): The name written on the gate. Defaults to "Hamming decoder".

    Returns:
        gate: Hamming decode
    """
    is_valid_input(kind)

    if kind == "both": 
        N += 1
    qc = HammingCircuit(N, ancillas=2*N-1)

    if kind != "bit":
        qc.h(list(range(2**N)))
    qc.append(Hamming_bit_decoder(N,read), [*range(2**N+N)])

    if kind == "both":
        if read==True:
            bits = [*list(range(2**(N-1))), *list(range(2**N + N, 2**N + 2*N - 1))]
        if read==False:
            bits = [*[i for i in range(2**(N-1)+N+1) if not is_power_2(i)],
                      *[*range(2**N + N, 2**N + 2*N - 1)]]
        qc.append(Hamming_bit_decoder(N-1), bits)
    
    return qc.to_gate(label=name)


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
            


def HammingSize(n,gate,kind):
    """Gives you the size of the circuit
    Args:
        n (int): lenght of the input message
        gate (str): it's either 'encoder' or 'decoder'
        kind (str): The kind argument must be one of bit, phase or both

    Returns:
        N (int): size of the gate
    """
    is_valid_input(kind)   
    N=HammingOrder(n, gate)

    if gate=='encoder':
        if kind=='both': return 2**(N+1)
        return 2**N
    if gate=='decoder':
        if kind=='both': return 2**(N+1) + 2*N + 1
        return 2**N + N
    
    raise Exception('Gate not valid, the input must be either \'encoder\' or \'decoder\'')

def xor(N):
    #This is the gate that calculates the xor of all the position with ones, this gives the position of the faulty qbit
    circ=HammingCircuit(N, ancillas=N)
    nqubits=2**N
    for i in range(1,nqubits):
        for j in range(0,N):
            if i & 2**j == 2**j: circ.cx(i,nqubits+j)
    return circ.to_gate(label='Initialize')

def correct(N):
    #This is the gate that corrects the faulty qbit
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

def Hamming_bit_decoder(N,read=True):
    #Hamming Gate resistant to bit-fips
    circ=HammingCircuit(N, ancillas=N)
    circ.append(xor(N),[*range(2**N+N)])
    circ.append(correct(N),[*range(2**N+N)])
    if read==True: circ.append(ReverseSwapper(N), [*range(2**N)])
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