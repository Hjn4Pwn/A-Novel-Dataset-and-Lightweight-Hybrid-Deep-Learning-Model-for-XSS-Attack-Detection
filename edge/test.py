import pandas as pd
import tensorflow as tf
import numpy as np

loaded_model = tf.keras.models.load_model('/home/pretrained_model.h5')

testX = pd.read_csv('/content/drive/MyDrive/_NCKH/testX.csv')
testY = pd.read_csv('/content/drive/MyDrive/_NCKH/testY.csv')  

testX_ = np.zeros((testX.shape[0],testX.shape[1]))
testX_[:testX.shape[0],:testX.shape[1]] = testX.values

testX_ = testX_.reshape(testX.shape[0],1,testX.shape[1],1)
testX_.shape

loss, accuracy = loaded_model.evaluate(testX_, testY)

print("Test Loss:", loss)
print("Test Accuracy:", accuracy)

predictions = loaded_model.predict(testX_)
