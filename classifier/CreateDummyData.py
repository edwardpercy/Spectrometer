import random
import numpy as np

DataArray = []
Timesteps = []
labels = []

outputArray = []
outputLabels = []

with open('RawData.txt') as f:
    lines = f.readlines()

count = 0
for l in lines:
    if count == 0:
        Timesteps = (l.split(","))
    else:
        data = l.split(",")
        labels.append(data[0])
        del data[0]
        DataArray.append(data)
    count += 1

for x in range(len(DataArray)):
    for y in range(len(DataArray[x])):
        DataArray[x][y] = DataArray[x][y].strip()

float_DataArray = np.array(DataArray)
float_DataArray = float_DataArray.astype(float)



#Generate random dummy data based off rawdata
for x in range(100):
    for y in range(3):
        temp = float_DataArray[y]
        #for z in range(len(temp)):
        temp = np.multiply(temp,random.uniform(0.8, 1.2))
        temp = np.round(temp,2)
        string_temp = list(map(str, temp))
        outputLabels.append(y)
        #string_temp.insert(0,labels[y])
        outputArray.append(string_temp)


with open('output.txt', 'w') as f:
    for x in outputArray:
        for y in x:
            f.write(y+ ',')
        f.write('\n')
with open('outputLabels.txt', 'w') as f:
    for x in outputLabels:
        f.write(str(x) + "\n")
        

