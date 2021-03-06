
from google.colab import files
uploaded  = files.upload()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM 
from keras.layers import Dense
import io
from sklearn.metrics import mean_squared_error

df = pd.read_csv(io.BytesIO(uploaded['baldwin_pump_data.csv']))
df

null_row = []
for i in range(0,len(df),2):
  null_row.append(i)

data = df.drop(null_row, axis=0)

index = []
for i in range(0,len(data)):
  index.append(i)
data.index = index

timestamp = []
for i in range(0 , len(data)):
  temp = data['Timestamp'][i].split("/")
  month = temp[0]
  date = temp[1]
  year = temp[2].split(" ")[0]
  time = temp[2].split(" ")[1]
  sample = "19"+year + "-" + month + "-" + date +  " " + time
  sample = pd.to_datetime(sample , format="%Y-%m-%d %H:%M:%S")
  timestamp.append(sample)

data.index = timestamp
data.drop(['Timestamp'] , axis = 'columns'  , inplace=True)

data.fillna(0)

from sklearn.preprocessing import StandardScaler
import seaborn as sb

plt.figure(figsize=(16,8))
sb.distplot(data['BFP_SEAL_WATER_FLOW']);

plt.figure(figsize = (40,7))
plt.scatter(data.index , data['BFP_SEAL_WATER_FLOW'])

for i in data.keys():
  min = data[i].min()
  max = data[i].max()
  for j in range(0,len(data[i])):
    data[i][j] = (data[i][j] - min) / (max-min)

data = data.sort_index(ascending=True, axis=0)
data

plt.figure(figsize=(16,8))
sb.distplot(data['BFP_SEAL_WATER_FLOW']);

plt.figure(figsize = (16,8))
correlation  = data.corr(method = "spearman")
sb.heatmap(correlation)

data.keys()
data.dropna()



stepwise_model = []
j = 0
for i in data.keys():
  features = i
  print("............" + features + ".............")
  # creating temporary dataframe with time variable and independant variable
  temp = pd.DataFrame()
  sample1 = data[features]
  sample1 = np.array(sample1 , dtype='float32')
  temp[features]  = sample1
  temp.index = data.index
  print("length of data", len(temp))
  #cleaning the data
  temp.dropna(inplace=True)
  print("lenghth after cleaning " , len(temp))
  #spliting of data for training and validation
  limit = int(len(temp)*0.8)
  training_data = temp[features][:limit]
  validation_data = temp[features][limit:]
  print("lenght of training data : " , len(training_data))
  print("length of validation data : " , len(validation_data))
  x_train = []
  y_train = []
  for i in range(50,len(training_data)):
    x_train.append(training_data[i-50:i])
    y_train.append(training_data[i])
  #reshaping data 
  x_train, y_train = np.array(x_train), np.array(y_train)
  x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1] ,1))
  print("shape of training data : " , x_train.shape)
  print("shape of dependant variable  :" , y_train.shape)
  # model defination
  features = Sequential()
  features.add(LSTM(units=50, return_sequences=True, input_shape= x_train[1].shape))
  features.add(LSTM(units=50))
  features.add(Dense(1))
  features.compile(loss='mean_squared_error', optimizer='adam')
  features.fit(x_train, y_train, epochs=1, batch_size=1)
  print(features.summary())
  stepwise_model.append(features)
  #prepare data for testing phase
  x_test , y_test = [] , []
  for i in range(50,len(validation_data)):
   x_test.append(validation_data[i-50:i])
   y_test.append(validation_data[i])
  x_test = np.array(x_test)
  #reshaping testing data
  x_test = np.reshape(x_test, (x_test.shape[0],x_test.shape[1],1))
  print("shape of testing data : " , x_test.shape)
  # predict testing data
  prediction = features.predict(x_test) 
  # checking accuracy of model
  print("mean_squared_error " , mean_squared_error(y_test , prediction))























