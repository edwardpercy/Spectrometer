import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
# Import BinaryRelevance from skmultilearn
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px


from sklearn import decomposition
from sklearn import datasets
from skmultilearn.problem_transform import BinaryRelevance

# Import SVC classifier from sklearn
from sklearn.svm import SVC

#To save model
from joblib import dump, load

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
n_samples = len(x_train)
n_features = len(x_test)


df = px.data.iris()
print (df.shape())

# features = ["sepal_width", "sepal_length", "petal_width", "petal_length"]

# fig = px.scatter_matrix(
#     df,
#     dimensions=features,
#     color="species"
# )
# fig.update_traces(diagonal_visible=False)
# fig.show()

# # Setup the classifier
# classifier = BinaryRelevance(classifier=SVC(), require_dense=[False,True])

# # Train
# classifier.fit(x_train, y_train)

# # Predict
# y_pred = classifier.predict(x_test)


# total = 0
# for x in range(len(y_test)):
#     try:
#         if int(str(y_pred[x]).split(')')[1].strip()) == int(y_test[x]):
#             total += 1
#     except:
#         pass


# print(f"{total} / {len(y_test)}")
# print((total / len(y_test)) * 100)

# dump(classifier, 'model.joblib') 