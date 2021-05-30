# Europe Qiskit Hackaton 2021

This repository was created for the Europe Qiskit Hackaton 2021. It focuses on re-purpusing classic error correction code and make it Quantum

# Quantum Hamming Code

Suppose you have a message |m> that is long n bits and you want to encode it in a noise resistant message |M>.

To do so you have to create a quantum cirucuit that is big enough to be able to hold |M> and additional ancillas (ancillas are required only for the syndrome).

To know how big has to be the circuit call the function 

```python
HammingSize(n,gate,kind):
    """Gives you the size of the circuit
    Args:
        n (int): lenght of the input message
        gate (str): it's either 'encoder' or 'decoder'
        kind (str): The kind argument must be one of bit, phase or both

    Returns:
        N (int): size of the gate
    """
    
HammingOrder(n):
    """Gives you the order of the Hamming gate as a function of n

    Args:
        n (int): lenght of the input message

    Returns:
        N (int): order of the Hamming gate
    """
```

Once you know how big is the circuit you can use the gates

```python
Hamming_encode(N):
    """Returns a hamming encoding circuit

    Args:
        N (int): Order of the hamming code used, acts on 2^N qubits
        kind (str, optional): Set to "bit" for correcting bit flip errors,
        "phase" for correcting phase flip errors, "both" corrects both errors. 
        Defaults to "both".

    Returns:
        Gates: The gates composing the circuit
    """

Hamming_decode(N, kind="both",read=True, name="Hamming decoder"):
    """It corrects the output, if you don't want to read the output just write read=False, that way
    the bits don't get switched

    Args:
        N (int): The order of the Hamming code
        kind (str): The kind argument must be one of bit, phase or both. Defaults to "both".
        read (bool): If True returns the output on the first qbits, otherwise it doesn't switch the output. Defaults to True.
        name (str): The name written on the gate. Defaults to "Hamming decoder".

    Returns:
        gate : Hamming decode
    """

# Reed-Solomon
