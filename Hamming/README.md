## Folder structure  

This folder contains the implementation and the test of the quantum Hamming code

`Hamming.py`: Module containing the implementation of the encoder and decoder of the Hamming code  

`Hamming_test.ipynb`: Notebook containing the testing of the Hamming code

## Quantum Hamming Code

Suppose you have a message |m> that is long n bits and you want to encode it in a noise resistant message |M>.

To do so you have to create a quantum circuit that is big enough to be able to hold |M> and additional ancillas (ancillas are required only for the syndrome).

To know how big has to be the circuit call the function 

```python
def HammingSize(n, gate, kind):
    """Gives you the number of qubits that must be present in the circuit
    Args:
        n (int): lenght of the input message
        gate (str): It's either 'encoder' or 'decoder'
        kind (str): The kind argument must be one of bit, phase or both

    Returns:
        n (int): Number of qubits required for the circuit
    """

def HammingOrder(n):
    """Gives you the order of the Hamming gate as a function of n

    Args:
        n (int): lenght of the input message

    Returns:
        N (int): order of the Hamming gate
    """
```

Once you know how big is the circuit you can use the gates

```python
def HammingEncode(N, kind="both", name="Hamming encoder"):
    """Returns a hamming encoding circuit of order N, to see which is the value
    of N required to encode n qubits you can use the HammingOrder function. 
    To see the number of input qubits required for this circuit you can call 
    the function HammingSize()

    Args:
        N (int): Order of the hamming code used, acts on 2^N qubits
        kind (str, optional): Set to "bit" for correcting bit flip errors,
        "phase" for correcting phase flip errors, "both" corrects both errors. 
        Defaults to "both".

    Returns:
        Gates: Hamming encode
    """

def HammingDecode(N, kind="both", read=True, name="Hamming decoder"):
    """It corrects the output, if you don't want to read the output just write read=False, that way
    the bits don't get switched.
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
```
