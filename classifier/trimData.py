# Import Module
from calendar import c
import os
from tabnanny import verbose
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize
from sklearn.neural_network import MLPClassifier
# Import BinaryRelevance from skmultilearn
from sklearn.neighbors import KNeighborsClassifier
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.gaussian_process import GaussianProcessClassifier
from skmultilearn.adapt import BRkNNaClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier

# Import SVC classifier from sklearn
from sklearn.svm import SVC

#To save model
from joblib import dump, load



# Folder Pa th
path = "C:/Users/Edward/Documents/Spectrometer/classifier/Spectro_Data"
  
# Change the directory
os.chdir(path)
  
# Read text File
  

labels = [1,2,3,4,5]
Datalabels = []
allData = []

def read_text_file(file_path):
    with open(file_path, 'r') as f:
        temp = []
        for line in f:
            temp.append(float(line))
        allData.append(temp)
        

        
def normalise(input):
    output = input
    count = 0
    minval = min(input)
    maxval = max(input)
    for x in range (len(input)):
        count += 1
        output[x] = (input[x]-minval)/(maxval-minval)
 
    return output
  
# iterate through all file
for file in os.listdir():
    # Check whether file is in text format or not
    if file.endswith(".txt"):
        file_path = f"{path}/{file}"
        Datalabels.append(int(file[0])+1)
        # call read text file function
        read_text_file(file_path)
    print("File read")

count = 0
for x in allData:
    Datalen = len(x)
 
    combLength = Datalen - 141999
    combDist = (Datalen / combLength)

    for t in range (combLength-1, 0,-1):
        allData[count].pop(round(t * combDist))
       
    
    allData[count] = normalise(allData[count])
    print("Data normalised")  


    count += 1

labels = np.array(labels)
labels = labels.astype(int)

Datalabels = np.array(Datalabels)
Datalabels = Datalabels.astype(int)

allData = np.array(allData)
allData = allData.astype(float)



x_train, x_test, y_train, y_test = train_test_split(allData, Datalabels, test_size = 0.3, random_state = 4)
n_samples = len(x_train)
n_features = len(x_test)


# Setup the classifier
# classifier = BinaryRelevance(classifier=SVC(), require_dense=[False,True])
# classifer = MLPClassifier(hidden_layer_sizes = (10000, ), activation = 'tanh',
#                             solver = 'sgd', alpha=0.01, max_iter=10000,
#                             shuffle = True, learning_rate='adaptive',
#                             nesterovs_momentum = True,
#                              verbose=1)
classifer =  BinaryRelevance(classifier=KNeighborsClassifier(3), require_dense=[False,True])

print("TRAINING")
# Train
classifer.fit(x_train, y_train)
print("TRAINED")
# Predict
y_pred = classifer.predict(x_test)


total = 0
for x in range(len(y_test)):
    try:
        if int(str(y_pred[x]).split(')')[1].strip()) == int(y_test[x]):
            total += 1
    except:
        pass


print(f"{total} / {len(y_test)}")
print((total / len(y_test)) * 100)

dump(classifer, 'spectro_model.joblib') 

print(len(allData))
y_pred = classifer.predict(allData)
print(y_pred.data)

print(Datalabels)

#blue canal distilled green red
#  1    2       3       4    5