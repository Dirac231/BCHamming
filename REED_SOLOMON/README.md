## Quantum Reed-Solomon 
The file `RS.py` contains the implementation of a general Quantum Reed Solomon (QRS) decoder.
  
It is designed so that everything is a function of the lenght of the sent message. In order to use the encoder you will need a way to initialize a state of your chosen number of Qbtis, you can do this either through a file `states.txt` or directly, by declaring a list of coefficients, for example:

```python
initial_state = [ [1,0],[1,0],[0,1]]
```
Will initialize the state `|0>|0>|1>`. Please note that in order to run simulations, you'll need a IBM-q account togheter with a token. The encoding of the state is done by the function:

```python
def encoder(initial_state):
    """Takes a message and return the circuit that encodes it.
    Input: list of binary lists, as initial_state = [ [1,0],[1,0],[0,1]]
    Returns: encoding circuit
    """
```
which by default returns the encoding circuit. The decoding happens inside the function:

```python
def decoder(qc):
    """Takes the encoding circuit, computes the syndrome and corrects the message.
    Input: quantum circuit after encoding
    Returns: decoding circuit, retrieved message, outcomes of measurements, syndrome.
    """
```
The simulation function used to retrieve the syndrome when calling `get_syndrome(qc)` or `get_qbits(qc)` is:

```python
def simulate(qc):
    """Simulates the circuit using the cloud-computing services of IBMq, this is always the recommended choice to run simulations"""
    provider = IBMQ.get_provider(hub='ibm-q')
    backend=provider.get_backend('simulator_mps')
    result = execute(qc, backend,shots=shots).result()
    print('Simulation Success: {}'.format(result.success))
    print("Time taken: {} sec".format(result.time_taken))
    counts = result.get_counts(0)
    return counts
```

## Installation
To clone the repository: `git clone https://github.com/Dirac231/BCHamming/`  

First, run `python3 -m pip install -r requirements.txt`. After that, if you wish to encode using a file, place the file `RS.py` in the same directory as `states.txt`, or alternatively, simply declare the variable `initial_state` as before. You can then use the functions inside of the file `RS.py`
