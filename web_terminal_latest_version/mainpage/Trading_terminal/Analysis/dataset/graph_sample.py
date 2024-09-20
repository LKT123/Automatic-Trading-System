import pandas as pd
import datetime
import pytz
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

df = pd.read_csv("dataset/qqq_23Y_test_data_1day.csv")
df.drop(["Unnamed: 0"],  axis=1, inplace=True)
df = df[df['Time'] >= 20080601]
df.reset_index(drop=True, inplace=True)
df['%Change'] = (df['Close'] - df['Open'])/df['Open']
df['%Shift'] = (df['High'] - df['Close'])/df['Open']



print(df.head())

# Draw the price graph
#plt.figure(figsize = (18,9))
# plt.plot(range(df.shape[0]),(df['Low']+df['High'])/2.0)
# plt.xticks(range(0,df.shape[0],500),df['Time'].loc[::500],rotation=45)
# plt.xlabel('Date',fontsize=18)
# plt.ylabel('Mid Price',fontsize=18)
# plt.show()


train_data = df[:len(df)-800]
test_data = df[len(df)-800:]
# Scale the data to be between 0 and 1
# When scaling remember! You normalize both test and train data with respect to training data
# Because you are not supposed to have access to test data
scaler = MinMaxScaler()
#train_data = train_data.reshape(-1,1)
#test_data = test_data.reshape(-1,1)



percent_change = train_data['%Change']
percent_shift = train_data['%Shift']

# Train the Scaler with training data and smooth data
smoothing_window_size = 365
for di in range(0,len(df),smoothing_window_size):
    scaler.fit(percent_change[di:di+smoothing_window_size,:])
    percent_change[di:di+smoothing_window_size,:] = scaler.transform(percent_change[di:di+smoothing_window_size,:])


# You normalize the last bit of remaining data
scaler.fit(train_data[di+smoothing_window_size:,:])
train_data[di+smoothing_window_size:,:] = scaler.transform(train_data[di+smoothing_window_size:,:])
