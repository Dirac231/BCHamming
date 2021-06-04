## Folder structure  

This folder contains the implementation and the test of the quantum Hamming code

`Hamming.py`: Module containing `HammingEncode()` and `HammingDecode()` and it's the one well commented

`Hamming_all.py`: Module containing all the functions that have been used to make `Hamming.py`

`Hamming_exampe.ipynb`: Example code, go take a look at that to understand how everything works

## General nomenclature

Suppose you have a message |m> that is long n bits and you want to encode it in a noise resistant message |M>.

To do so you have to create a quantum circuit that is big enough to be able to hold |M> and additional ancillas (ancillas are required only for the syndrome).


# How to use the gates
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

# How big are these gates?

Every gate returned by these two functions has the `size` attribute, which tells how big the gate is
