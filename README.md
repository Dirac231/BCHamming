# Europe Qiskit Hackaton 2021

This repository was created for the Europe Qiskit Hackaton 2021. It focuses on re-purpusing classic error correction code and make it Quantum

# Quantum Hamming Code

Suppose you have a message $\ket{m}$ that is long $n$ bits and you want to encode it in a noise resistant message $\ket M$.

To do so you have to create a quantum cirucuit that is big enough to be able to hold $\ket M$ and additional ancillas (ancillas are required only for the syndrome).

To know how big has to be the circuit call the function 

```python
HammingSize(n,gate):
"""
	args:
		n: lenght of the input message
		gate: it's either 'encoder' or 'decoder'
	returns:
		N: size necessary of the circuit
"""
```

Once you know how big is the circuit you can use the gates

```python
HammingEncode(N):
"""
	args:
		N: is the output of the Hamming size
	returns:
		A gate that is N qbits Big
"""

HammingCorrect(N):
"""
	args:
		N: is the output of the Hamming size
	returns:
		A gate that is N qbits Big
"""

HammingDecode(N):
"""
	args:
		N: is the output of the Hamming size
	returns:
		A gate that is N qbits Big
"""
```

# Reed-Solomon
