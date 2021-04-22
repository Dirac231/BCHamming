Questo file ha uno scopo riassuntivo per la teoria dei codici Hamming e BCH

HAMMING:

1)Il codice Hamming costituisce un encoding dalle parole binarie di lunghezza K verso quelle di lunghezza N.
2)Partendo dall'insieme https://latex.codecogs.com/gif.latex?B_%7Bk%7D delle parole binarie lunghe K, il codice Hamming genera l'insieme https://latex.codecogs.com/gif.latex?G%28B_%7Bk%7D%29
  attraverso un operatore lineare https://latex.codecogs.com/gif.latex?G (rispetto alla somma bit-bit).
3)L'operatore lineare inverso di https://latex.codecogs.com/gif.latex?G viene chiamato https://latex.codecogs.com/gif.latex?H, il ricevitore di un messaggio codificato con
  l'operatore https://latex.codecogs.com/gif.latex?G riceve la stringa: https://latex.codecogs.com/gif.latex?r%20%3D%20Gt%20%5Coplus%20n dove https://latex.codecogs.com/gif.latex?t e' la stringa 
  di lunghezza https://latex.codecogs.com/gif.latex?k che si vuole trasmettere, mentre https://latex.codecogs.com/gif.latex?n e' il rumore esterno che cambia i bit del messaggio inviato.
4) Il ricevitore costruisce l'operatore https://latex.codecogs.com/gif.latex?H tale che https://latex.codecogs.com/gif.latex?HG%20%3D%200, in questo modo si arriva
 
