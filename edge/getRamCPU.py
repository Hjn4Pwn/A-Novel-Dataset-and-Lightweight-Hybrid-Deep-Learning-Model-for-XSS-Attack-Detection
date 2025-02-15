import pandas as pd
import tensorflow as tf
import numpy as np

from google.colab import drive
drive.mount('/content/drive')

loaded_model = tf.keras.models.load_model('/home/pretrained_model.h5')

testX = pd.read_csv('/content/drive/MyDrive/_NCKH/testX.csv')

testX_ = np.zeros((testX.shape[0],testX.shape[1]))
testX_[:testX.shape[0],:testX.shape[1]] = testX.values

i=10;
while i :
  prediction = loaded_model.predict(testX_.reshape(testX.shape[0],1,testX.shape[1],1))
  i=i-1


