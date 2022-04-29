
import numpy as np


#To save model
from joblib import dump, load
import os

classifier = load('spectro_model.joblib') 

  
# Read text File

def read_text_file(file_path):
    with open(file_path, 'r') as f:
        temp = []
        for line in f:
            temp.append(float(line))
        x = temp
    
    Datalen = len(x)
 
    combLength = Datalen - 141999
    combDist = (Datalen / combLength)

    for t in range (combLength-1, 0,-1):
        x.pop(round(t * combDist))
       
    
    x = normalise(x)
    print("Data normalised")  

    x = np.array(x)
    x = x.astype(float)

    return x
        

        
def normalise(input):
    output = input
    count = 0
    minval = min(input)
    maxval = max(input)
    for x in range (len(input)):
        count += 1
        output[x] = (input[x]-minval)/(maxval-minval)
 
    return output
  

path = "C:/Users/Edward/Documents/Spectrometer/classifier/Spectro_Data"
file = "00.txt"

file_path = f"{path}/{file}"
data = read_text_file(file_path)



y_pred = classifier.predict(data)
print(y_pred.data[0])


#blue canal distilled green red
#  1    2       3       4    5