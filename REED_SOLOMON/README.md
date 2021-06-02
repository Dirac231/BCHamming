## Quantum Reed-Solomon 
The file `RS.py` contains the implementation of a general Quantum Reed Solomon (QRS) decoder.
  
It is designed so that everything is a function of the lenght of the sent message. In order to use the encoder you will need a way to initialize a state of your chosen number of Qbtis, you can do this either through a file `states.txt` or directly, by declaring a list of coefficients, for example:

```python
initial_state = [ [1,0],[1,0],[0,1]]
```
Will initialize the state `|0>|0>|1>`. Please note that in order to run simulations, you'll need a IBM-q account togheter with a token. The encoding of the state is done by the function:

```python
def encoder(initial_state):
    """Takes a message and return the circuit that encodes it"""
    qc = QuantumCircuit(encode_reg)
    for i in range(0,k_cl):
        qc.initialize(initial_state[i], i) 
    for i in range(k_cl*(K + 1), ENC-k_cl*K):
        qc.initialize(initial_state[i], i)
    for i in range(ENC - k_cl*K,ENC):
        qc.h(i)
    qc.append(inv_fourier, encode_reg[:ENC])
    return qc
```
which by default returns the encoding circuit. The decoding happens inside the function:

```python
def decoder(qc):
    """Takes the ecoding circuit, computes the syndrome and corrects the message"""
    qc.append(fourier, encode_reg[:ENC])
    for i in range(k_cl+1,k_cl*(K+1)+1):
        qc.cx(i-1, i+ENC-k_cl-1)
    for i in range(ENC -k_cl*K, ENC):
        qc.h(i)
    for i in range(ENC-k_cl*K-1,ENC-1):
        qc.cx(i+1, i+ENC-k_cl+1)
    for i in range(ENC -k_cl*K-1, ENC-1):
        qc.h(i+1)
    qc.append(inv_fourier, encode_reg[:ENC])
 
    syn = get_syndrome(qc)
    bf,pf,x = error_locator(syn)
    if(bf != "1" or x[:k_cl*K] != "0"*k_cl*K):
        for i in range(len(bf)):
            if (bf[i] == "1"):
                qc.x(i)
    if (pf != "1" or x[k_cl*K:] != "0"*k_cl*K):
        for i in range(ENC):
            qc.h(i)

        for i in range(len(pf)):
            if (pf[i] == "1"):
                qc.z(i)

        for i in range(ENC):
            qc.h(i)
    qc.append(fourier, encode_reg[:ENC])
    
    message,occurrences = get_qbits(qc)
    occurrences = zip([x[:3][::-1] for x in occurrences.keys()] , list(occurrences.values()))
    D = defaultdict(int)
    for k,v in occurrences:
        D[k]+= int(v)
    occurrences = dict(D)
    
    return qc,message,x,occurrences
```
By default, this function will return the full decoding circuit and the retrieved message with the occurences of the measurements. The simulation function used to retrieve the syndrome when calling `get_syndrome(qc)` or `get_qbits(qc)` is:

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
