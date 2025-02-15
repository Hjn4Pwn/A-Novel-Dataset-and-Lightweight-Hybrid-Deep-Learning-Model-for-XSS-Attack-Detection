import pandas as pd
import tensorflow as tf
import numpy as np

import time

from google.colab import drive
drive.mount('/content/drive')

loaded_model = tf.keras.models.load_model('/home/pretrained_model.h5')

testX = pd.read_csv('/content/drive/MyDrive/_NCKH/testX.csv')
testY = pd.read_csv('/content/drive/MyDrive/_NCKH/testY.csv')

testX_ = np.zeros((testX.shape[0],testX.shape[1]))
testX_[:testX.shape[0],:testX.shape[1]] = testX.values

testX_ = testX_.reshape(testX.shape[0],1,testX.shape[1],1)


loss, accuracy = loaded_model.evaluate(testX_, testY)

# print("Test Loss:", loss)
# print("Test Accuracy:", accuracy)

start_time = time.time()
prediction = loaded_model.predict(testX_)
end_time = time.time()
testingTime = end_time - start_time
print(testingTime)

