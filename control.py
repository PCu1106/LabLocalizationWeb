import subprocess
import time
from filelock import FileLock
import sys
import os 
import io

#關警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # '0' (default) to show all logs, '2' to suppress INFO messages, '3' to suppress INFO and WARNING messages
os.environ['CUDA_VISIBLE_DEVICES'] = "0"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, line_buffering=True)
input_csv_file = 'rssi_buffer.csv'
lock_file = 'l.lock' 


def read_locked_file():
#def read_locked_file(input_csv_file, lock_file, retries=10, retry_wait=1):
    # while retries > 0:
    #     try:
    #         lock = FileLock(lock_file)
    #         with lock:
    #             with open(input_csv_file, 'r') as input_file:
    #                 data = input_file.read()
    #         return data
    #     except (FileLock.FileLockException, FileNotFoundError):
    #         print("File is locked or not found, waiting and retrying...")
    #         time.sleep(retry_wait)
    #         retries -= 1

    # print("Exceeded maximum retry attempts. File could not be read.")
    # return None  # Or handle the failure accordingly
    with open(input_csv_file, 'r') as input_file:
        for line in input_file:
            return line


#print("troy2_control")
arguments = sys.argv  # argument[1]"哪種方法", argument[2]"模擬 or realtime", argument[3]"rssi值", argument[4]"粒子數" , argument[5]"粒子數"
if(int(arguments[1])==0): # 用RSSI
    #print("control.py"+arguments[3])
    command = ['python', './ANN.py', arguments[2], arguments[3], arguments[4]]
    rssi_history = arguments[3]
    while True:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        # rssi = read_locked_file(input_csv_file, lock_file)
        rssi = read_locked_file()
        if(rssi!=rssi_history):
            command = ['python', './ANN.py', arguments[2], rssi, arguments[4]]
            output = process.stdout.readline()
        else:
            continue
        if output == '' and process.poll() is not None: break 
        if output: print(output.strip())
        sys.stdout.flush()


elif(int(arguments[1])==1): # 用影像
    if(int(arguments[2])==0):
        #用相對路徑 ~/yolov7/realtimeD.py 會錯不知道為啥
        command = ['python', '/home/mcs/yolov7/realtimeD.py', '--weights', '/home/mcs/yolov7/weights/yolov7.pt', '--source', '/home/mcs/yolov7/datasets/0408_testdata/101N.mp4', '--nosave']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None: break 
            if output: print(output.strip())
            sys.stdout.flush()
    elif(True):
        command = ['python', '/home/mcs/yolov7/realtimeD.py', '--weights', '/home/mcs/yolov7/weights/yolov7.pt', '--source', '/home/mcs/yolov7/datasets/0408_testdata/101N.mp4', '--nosave']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None: break 
            if output: 
                output_list = output.strip().split(', ')
                first_element = output_list[0].strip('[').strip('"')
                prob = output_list[1]
                print(first_element)
            sys.stdout.flush()


elif(int(arguments[1])==3): # 用ANN_contrast.py
    command = ['python', './ANN_contrast.py', arguments[2], arguments[3], arguments[4]]
    while True:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        rssi = read_locked_file(input_csv_file, lock_file)
        command = ['python', './ANN_contrast.py', arguments[2], rssi, arguments[4]]
        output = process.stdout.readline()
        if output == '' and process.poll() is not None: break 
        if output: print(output.strip())
        sys.stdout.flush()


elif(False): # 用其他方法(待).......................................................................
    command = ['python', './ANN_contrast.py', arguments[2], arguments[3], arguments[4]]
    while True:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        rssi = read_locked_file(input_csv_file, lock_file)
        command = ['python', './ANN_contrast.py', arguments[2], rssi, arguments[4]]
        output = process.stdout.readline()
        if output == '' and process.poll() is not None: break 
        if output: print(output.strip())
        sys.stdout.flush()