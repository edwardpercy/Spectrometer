import numpy as np
from sklearn.model_selection import train_test_split

# Import BinaryRelevance from skmultilearn
from skmultilearn.problem_transform import BinaryRelevance

# Import SVC classifier from sklearn
from sklearn.svm import SVC

#To save model
from joblib import dump, load

classifier = load('model.joblib') 

data = []
labels = []

with open('output.txt') as f:
    lines = f.readlines()
    for l in lines:
        data.append(l.split(','))

with open('outputLabels.txt') as f:
    lines = f.readlines()
    for l in lines:
        labels.append(l)


for x in range(len(data)):
    for y in range(len(data[x])):
        data[x][y] = data[x][y].strip()
        if data[x][y] == "":
            del data[x][y]
        
labels = np.array(labels)
labels = labels.astype(int)

data = np.array(data)
data = data.astype(float)

x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size = 0.3, random_state = 4)

# Predict
y_pred = classifier.predict(data)

print(y_pred.data)