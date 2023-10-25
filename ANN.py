from ctypes import *
import random
from os import listdir
from os.path import isfile, isdir, join
#from socket import PF_CAN
import time
from queue import Queue
from collections import defaultdict
import csv
import pandas as pd
import numpy as np
import ast
import json
import time
#import imagehash
import hashlib
import math
import sys
import shlex
import tensorflow as tf
from sklearn import datasets
import numpy as np
import csv
import pandas as pd
import os
import Wireless_Particle_Filter as PF



position_label=['101','102','103','104','105','106','107','108','109','110','111',  '201','211','301','311','401','411','501','511', '601','602','603','604','605','606','607','608','609','610','611', '701','711','801','811','901','911','1001','1011',  '1101','1102','1103','1104','1105','1106','1107','1108','1109','1110','1111']


arguments = sys.argv       # arguments[0] 好像被保留
#if (False):
if (int(arguments[1])==0): #選用模擬.................................................................................
    print("troy2_ANN.py_simulation")
    new_model = tf.keras.models.load_model('X_model_0409.h5')
    y_pred=np.array([])
    csv_file_path = "/home/mcs/troy2/walk_data/wireless_training_1002.csv"
    with open(csv_file_path, "r") as file:
        reader = csv.reader(file) # Create a CSV reader object
        next(reader)              # Skip the header row
        for row in reader:        # Read the CSV file row by row
            columns = row[1:]     # Skip the first column (label) by slicing the row list
            Wireless_RssiData = [float(column) for column in columns] # Convert the remaining columns to float values
            y_pred = new_model.predict([Wireless_RssiData], verbose=0) # Call new_model.predict() with the Wireless_RssiData as input
            #print(y_pred)
            time.sleep(1)
            dict={}
            for i in range (len(y_pred[0])):
                dict[position_label[i]]=int(y_pred[0][i]*100)
            count=int(arguments[3])
            #print(final_position)
            final_position=PF.calculate(dict,count)
            print(final_position)
            sys.stdout.flush()
            
#elif(True): #測試用
elif(int(arguments[1])==1): #選用realtime...............................................................................
    #print("troy2_ANN.py_realtime")
    #Wireless_Test = {'Beacon_1': 0.459016393, 'Beacon_2':0.557377049, 'Beacon_3': 0.344262295,
    #             'Beacon_4':0.37704918, 'Beacon_5': 0.540983607,  'Beacon_7': 0.655737705, }
    beacon_rssi=str(arguments[2])
    #print("troy2_ANN.py1"+beacon_rssi)
    Wireless_Test=beacon_rssi.replace("q","")
    print("troy2_ANN.py2"+Wireless_Test)
    sys.stdout.flush()
    Wireless_Test=json.loads(Wireless_Test)
    

    Wireless_RssiData = np.array([])
    for beacon_id, RSSI in Wireless_Test.items():
        RSSI=float(RSSI)
        Wireless_RssiData=np.append(Wireless_RssiData,RSSI)

    new_model = tf.keras.models.load_model('X_model_0409.h5')
    y_pred=new_model.predict([[Wireless_RssiData[0],Wireless_RssiData[1],Wireless_RssiData[2],Wireless_RssiData[3],Wireless_RssiData[4],Wireless_RssiData[5]],],verbose = 0)
    dict={}
    for i in range (len(y_pred[0])):
        dict[position_label[i]]=int(y_pred[0][i]*100)
    count=int(arguments[3])
    final_position=PF.calculate(dict,30000) #測試用
    #print(final_position)


#y_pred_class = np.argmax(y_pred, axis=1)
#print(y_pred_class)
#final_position=position_label[y_pred_class[0]]
#print(Wireless_Test_hash)
# dict={}
# for i in range (len(y_pred[0])):
#     dict[position_label[i]]=int(y_pred[0][i]*100)
    
# #print(dict)

# count=int(sys.argv[2])

# #print(final_position)
# final_position=PF.calculate(dict,count)
# print(final_position)









'''
final_position_numbers = sum(c.isdigit() for c in final_position)
wireless_path = f'./walk_data/'
#用LR的set來做KNN  判斷是在這個位置的 中間 左 右

Wireless_Train_LR = pd.read_csv(join(wireless_path, 'wireless_training_LR.csv'))
list_of_Wireless_Train_LR_hash = []
train_label_LR = []
for i in range(len(Wireless_Train_LR)):
    Wireless_Train_LR_row = Wireless_Train_LR.iloc[i].to_dict()
    Wireless_Train_LR_label = Wireless_Train_LR_row['label']
    numbers = sum(c.isdigit() for c in Wireless_Train_LR_label)
    if(final_position_numbers==numbers and final_position in Wireless_Train_LR_label ):  #605的話  查看set中的 605L 605 605R
        train_label_LR.append(Wireless_Train_LR_label)
        Wireless_Train_LR_row.pop('label', None)
        # device1 hash encode
        Wireless_Train_LR_hash = np.array([])
        for beacon_id, RSSI in Wireless_Train_LR_row.items():
            hash_ = text_hash(beacon_id, RSSI)  # 每一個RSSI值被hash成一個大小512的array
            if len(Wireless_Train_LR_hash) < 1:
                Wireless_Train_LR_hash = hash_
            else:
                # 每個RSSI hash完的512array 8個array數值疊加起來(大小還是512)
                Wireless_Train_LR_hash = Wireless_Train_LR_hash + hash_

        Wireless_Train_LR_hash = signed_encode(Wireless_Train_LR_hash)
        list_of_Wireless_Train_LR_hash.append(Wireless_Train_LR_hash)

k_top_similarity = [0.0]*K
voter = [0.0]*K


for k in range(len(list_of_Wireless_Train_LR_hash)):
    sim_ = similarity(
        list_of_Wireless_Train_LR_hash[k], Wireless_Test_hash)
    if sim_ > (min(k_top_similarity)):
        k_top_similarity[k_top_similarity.index(
            min(k_top_similarity))] = sim_
        voter[k_top_similarity.index(
            min(k_top_similarity))] = train_label_LR[k]


predict_label.append(max(voter, key=voter.count))  # 票票等值
# predict_label.append(vote.index(max(vote))) # 票票不等值 similarity 為權重
print( max(voter, key=voter.count))
if(count==0):
    accuracy=[]
    accuracy.append(max(voter, key=voter.count))
    np.save('accuracy', accuracy)
else:
    accuracy = np.load('accuracy.npy')
    accuracy=np.append(accuracy,(max(voter, key=voter.count)))
    np.save('accuracy', accuracy)
    
    
if(count==5):
    result={}
    for key in accuracy:
        result[key]=result.get(key,0)+1
    print(result)
#print("final position:",final_position)
#print("predict:",final_position)
'''