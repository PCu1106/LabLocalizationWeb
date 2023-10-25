from ctypes import *
import random
from os import listdir
from os.path import isfile, isdir, join
#from socket import PF_CAN
import time
from queue import Queue
from collections import defaultdict

import pandas as pd
import numpy as np
import ast
import json
#import imagehash
import hashlib
import math
import sys
import shlex
import tensorflow as tf
from sklearn import datasets
import numpy as np
import pandas as pd
import os
import Wireless_Particle_Filter as PF

import csv
import json


position_label=['101','102','103','104','105','106','107','108','109','110','111',  '201','211','301','311','401','411','501','511', '601','602','603','604','605','606','607','608','609','610','611', '701','711','801','811','901','911','1001','1011',  '1101','1102','1103','1104','1105','1106','1107','1108','1109','1110','1111']
# Wireless_Test = {'Beacon_1': 0.459016393, 'Beacon_2':0.557377049, 'Beacon_3': 0.344262295,
#              'Beacon_4':0.37704918, 'Beacon_5': 0.540983607,  'Beacon_7': 0.655737705, }
base_csv_filename  = "position_history/history"
config_filename  = "position_history/config.json"
rows_per_file = 10

def load_config():
    try:
        with open(config_filename, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {"file_counter": 1, "row_count": 0}

def save_config(config):
    with open(config_filename, "w") as config_file:
        json.dump(config, config_file)

def write_row_to_csv(row_data, config):
    csv_filename = f"{base_csv_filename}_{config['file_counter']}.csv"
    
    if config['row_count'] % rows_per_file == 0:
        with open(csv_filename, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Ground Truth Position", "Prediction Position", "RSSI Value 1", "RSSI Value 2", "RSSI Value 3", "RSSI Value 4", "RSSI Value 5", "RSSI Value 6"])
    
    with open(csv_filename, "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(row_data)
        
    config['row_count'] += 1
    if config['row_count'] % rows_per_file == 0:
        config['file_counter'] += 1


arguments = sys.argv   
if(int(arguments[1])==1): #選用realtime...............................................................................
    # Wireless_Test = {'Beacon_1': 0.459016393, 'Beacon_2':0.557377049, 'Beacon_3': 0.344262295,
    #              'Beacon_4':0.37704918, 'Beacon_5': 0.540983607,  'Beacon_7': 0.655737705, }
    beacon_rssi=str(arguments[2])
    #print(str(arguments[4]))
    Wireless_Test=beacon_rssi.replace("q","")
    #print("troy2_ANN_contrast.py"+Wireless_Test)
    sys.stdout.flush()
    Wireless_Test=json.loads(Wireless_Test)
    
    Wireless_RssiData = np.array([])
    for beacon_id, RSSI in Wireless_Test.items():
        RSSI=float(RSSI)
        Wireless_RssiData=np.append(Wireless_RssiData,RSSI)

    #print("troy2_ANN_contrast.py "+str(int(Wireless_RssiData[6])))

    new_model = tf.keras.models.load_model('X_model_0409.h5')
    y_pred=new_model.predict([[Wireless_RssiData[0],Wireless_RssiData[1],Wireless_RssiData[2],Wireless_RssiData[3],Wireless_RssiData[4],Wireless_RssiData[5]],],verbose = 0)
    dict={}
    for i in range (len(y_pred[0])):
        dict[position_label[i]]=int(y_pred[0][i]*100)
    count=int(arguments[3])
    final_position=PF.calculate(dict,30000)
    print("ANN_contrast.py "+final_position +" Ground Truth: "+ str(int(Wireless_RssiData[6]) ))
    #print("ANN_contrast.py "+str(arguments[4]))
    #print(final_position)
    


    ###---------------------------------------------寫到position_history裡的csv檔做heat map----------------------------------
    # if(True):  
    if(final_position != int(Wireless_RssiData[6]) and int(Wireless_RssiData[6])!=0 ): #如果prediction 不等於 ground truth的時候
    # if(int(Wireless_RssiData[6]) != 0):
        #print("drawheatmap")
        config = load_config()
        # data = (101, 102, -70, -75, -80, -85, -90, -95)
        data = (int(Wireless_RssiData[6]), final_position, Wireless_RssiData[0], Wireless_RssiData[1], Wireless_RssiData[2], Wireless_RssiData[3], Wireless_RssiData[4], Wireless_RssiData[5])
        write_row_to_csv(data, config)
        save_config(config)
        
