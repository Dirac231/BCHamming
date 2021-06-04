from Hamming_all import *


def HammingEncode(n, kind="both", name="Hamming encoder"):
    """Returns a hamming encoding circuit capable of encodig at least n Qbits 
    To see the number of input qubits required for this circuit you can call 
    the function HammingSize()

    Args:
        N (int): Order of the hamming code used, acts on 2^N qubits
        kind (str): Set to "bit" for correcting bit flip errors,
        "phase" for correcting phase flip errors, "both" corrects both errors. 
        Defaults to "both".

    Returns:
        Gates: Hamming encode
    """
    is_valid_input(kind) #check if the kind of input is valid
    N=HammingOrder(n) #Calculates the order of the Hamming code

    #if you are not interestd in correcting both errors you can just return either the bit encoder or the
    #phase encoder from the file Hamming_all.py
    if kind !="both":
        Hammng_Encode=Hamming_bit_encoder(N,name=name,kind=kind)
        Hammng_Encode.size=HammingSize(n,gate='encoder',kind=kind)
        return Hammng_Encode
    
    #When kind=='both' this part can be optimized by not wasting bits that aren't used 
    #neither for messages bits nor for parity bits   
    qc = HammingCircuit(N+1, ancillas=0)

    #Put the encoders for bitflip in the circuit.
    #This part can be optimized by creating an encoder with fewer signal bits, but we didn't write this function
    qc.append(Hamming_bit_encoder(N, kind='bit'), [*range(2**N)])
    #if you have to correct both you need a Hamming cirucuit of a order higher.
    N += 1
    qc.append(Hamming_bit_encoder(N, kind='phase'), [*range(2**N)])

    #Add the size attribute, it says how big the gate is
    Hamming_Encode=qc.to_gate(label=name)
    Hamming_Encode.size=HammingSize(n,gate='encoder',kind=kind)
    
    return Hamming_Encode



def HammingDecode(n, kind="both", read=True, name="Hamming decoder"):
    """It corrects the output, if you don't want to read the output just write read=False.
    To see the number of input qubits required for this circuit you can call 
    the function HammingSize()


    Args:
        N (int): The order of the Hamming code
        kind (str): The kind argument must be one of bit, phase or both. Defaults to "both".
        read (bool): If True returns the output on the first qbits, otherwise it doesn't switch the output. Defaults to True.
        name (str): The name written on the gate. Defaults to "Hamming decoder".

    Returns:
        gate: Hamming decode
    """
    is_valid_input(kind) #check if the kind of input is valid
    N=HammingOrder(n) #Calculates the order of the Hamming code

    #if you are not interestd in correcting both errors you can just return either the bit decoder or the
    #phase encoder from the file Hamming_all.py
    if kind != 'both':
        Hamming_Decode=Hamming_bit_decoder(N,kind=kind,read=read,name=name)
        Hamming_Decode.size=HammingSize(n,gate='decoder',kind=kind)
        return Hamming_Decode
    
    #if you have to correct both you need a Hamming cirucuit of a order higher.
    #Also this can be optimized, to understand how look at Hamming Encode
    N += 1
    qc = HammingCircuit(N, ancillas=2*N-1)#define the circuit
 
    #add the hamming phase decoder
    qc.append(Hamming_bit_decoder(N,kind='phase',read=read,name=name), [*range(2**N+N)])

    #Don't even try to understand this code, all it does is linking the output of the phase decoder with
    #the output of the phase encoder in the correct qbits
    if read==True:
        bits = [*list(range(2**(N-1))), *list(range(2**N + N, 2**N + 2*N - 1))]
    if read==False:
        bits = [*[i for i in range(2**(N-1)+N+1) if not is_power_2(i)],
                    *[*range(2**N + N, 2**N + 2*N - 1)]]


    qc.append(Hamming_bit_decoder(N-1,kind='bit',read=read), bits)

    #Add the size attribute, it says how big the gate is
    Hamming_Decode=qc.to_gate(label=name)
    Hamming_Decode.size=HammingSize(n,gate='decoder',kind=kind)
    
    return Hamming_Decode

