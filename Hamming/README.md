## Folder structure  

This folder contains the implementation and the test of the quantum Hamming code

`Hamming.py`: Module containing the implementation of the encoder and decoder of the Hamming code  

`Hamming_test.ipynb`: Notebook containing the testing of the Hamming code

## General nomenclature

Suppose you have a message |m> that is long n bits and you want to encode it in a noise resistant message |M>.

To do so you have to create a quantum circuit that is big enough to be able to hold |M> and additional ancillas (ancillas are required only for the syndrome).

# How to know how big the circuit needs to be

To know how big has to be the circuit call the function. To so you have to call `HammingSize()`, it gives you the number of qubits that must be present in the circuit

```python
def HammingSize(n, gate, kind):
    """Gives you the number of qubits that must be present in the circuit
    Args:
        n (int): lenght of the input message
        gate (str): It's either 'encoder' or 'decoder'
        kind (str): The kind argument must be one of 'bit', 'phase' or 'both'

    Returns:
        N (int): Number of qubits required for the circuit
    """
```
Depending on the `gate` and the `kind` the result changes, if you use multiple gates on your circuit be sure to have the circuit at least as big as the biggest gate


# How to use the gates
Once you know how big is the circuit you can use the gates.
The function `HammingEncode()` returns a hamming encoding capable of encoding n Qbits
```python
def HammingEncode(n, kind="both", name="Hamming encoder"):
    """Returns a hamming encoding gate of order N.
    To see the number of input qubits required for this circuit you can call 
    the function HammingSize()

    Args:
        n (int): The number of Qbits of you non-encoded message
        kind (str, optional): Set to "bit" for correcting bit flip errors,
        "phase" for correcting phase flip errors, "both" corrects both errors. 
        Defaults to "both".

    Returns:
        Gates: Hamming encode
    """
```

If you want decode the Hamming code you just have to add the `HammingDecode` gate to your circuit.
If you don't want to read the output and you just want to correct an error assign `read=False`, that way the bits don't get switched for a easier readability.
```python
def HammingDecode(n, kind="both", read=True, name="Hamming decoder"):
    """
    Args:
        n (int): The number of Qbits of you non-encoded message
        kind (str): The kind argument must be one of 'bit', 'phase' or 'both'. Defaults to 'both'.
        read (bool): If True returns the output on the first qbits, otherwise it doesn't switch the output. Defaults to True.
        name (str): The name written on the gate. Defaults to "Hamming decoder".

    Returns:
        gate: Hamming decode
    """
```
