# Qiskit Hackathon Europe 2021

This repository was created for the Europe Qiskit Hackaton 2021. \
 \
 The project focuses on building a quantum version of the Hamming code and the BCH model. \
\
The official report is available [here](https://github.com/Dirac231/BCHamming/blob/main/Report.pdf)

## Folder structure

`Hamming\`: Contains the implementation and documentation of the quantum Hamming code  

`REED_SOLOMON\`: Contains the implementation and documentation of the quantum Reed Solomon  

`Slides.pdf`: Slides in pdf format of the Hackaton Project  

`Report.pdf`: Report of the Hackaton Project

`requirements.txt`: Required python packages to make the code work


## Installation and Usage
To use this package you just have to clone the repository: 

```
git clone https://github.com/Dirac231/BCHamming/
```

After cloning, execute 

```
python3 -m pip install -r requirements.txt
```

which will install all the required packages to run the code.   

After installing the libraries you can see the [wiki](https://github.com/Dirac231/BCHamming/wiki) to understand how to use the Hamming and Reed Solomon error correcting codes.

The purpose of the Hamming code is to be used when the errors are uncommon because it can only correct at most two of them.
The number of errors that the Reed-Solomon code is able to correct is proportional to the lenght of the message, making it the best choice for noisier scenarios.
