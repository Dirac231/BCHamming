# Europe Qiskit Hackaton 2021

This repository was created for the Europe Qiskit Hackaton 2021. It focuses on re-purpusing classic error correction code and make it Quantum

## Folder structure

`Hamming\`: Contains the implementation and documentation of the quantum Hamming code  

`REED_SOLOMON\`: Contains the implementation and documentation of the quantum Reed Solomon  

`Papers\`: Papers we found useful to complete the project, they are all open access  

`Slides.pdf`: Slides in pdf format of the Hackaton Project  

`requirements.txt`: Required python packages to make the code work


## Installation and Usage
To use this package you just have to clone the repository: `git clone https://github.com/Dirac231/BCHamming/`.  
After cloning, execute `python3 -m pip install -r requirements.txt` this will install all the required packages to run the library.   
Now that you have installed the library you can take a look at the [wiki](https://github.com/Dirac231/BCHamming/wiki) to learn how to use the Hamming and Reed Solomon error correcting codes.

In general the Hamming code should be used when the errors are rare because it can only correct at most two of them.  The Reed Solomon instead can correct more and more errors the longer the message is, but it also needs more qubits to encode the message, so it is the preferred choice for more noisy scenarios


## How we divided the work

We used the buit-in method of the github [projects](https://github.com/Dirac231/BCHamming/projects/1) to track and coordinate the work to do.
