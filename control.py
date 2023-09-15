import subprocess
import sys

arguments = sys.argv  # argument[1]"哪種方法" argument[2]"模擬 or realtime" argument[3]"rssi值"
print(arguments)
if(int(arguments[1])==0): # 用RSSI
    command = ['python', './ANN.py', arguments[2], arguments[3], arguments[4]]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None: break 
        if output: print(output.strip())
        sys.stdout.flush()
    

elif(int(arguments[1])==1): # 用影像
    if(int(arguments[2])==0):
        #用相對路徑 ~/yolov7/realtimeD.py 會錯不知道為啥
        ##python /home/mcs/yolov7/realtimeD.py --weights /home/mcs/yolov7/weights/yolov7.pt --source /home/mcs/yolov7/datasets/0408_testdata/101N.mp4 --nosave
        command = ['python', '/home/mcs/yolov7/realtimeD.py', '--weights', '/home/mcs/yolov7/weights/yolov7.pt', '--source', '/home/mcs/yolov7/datasets/0408_testdata/101N.mp4', '--nosave']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None: break 
            if output: print(output.strip())
            sys.stdout.flush()

    elif(int(arguments[2])==1):
        command = ['python', '/home/mcs/yolov7/realtimeD.py', '--weights', '/home/mcs/yolov7/weights/yolov7.pt', '--source', 'http://140.116.72.67:8080/yen', '--nosave']
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

if(int(arguments[1])==2): # 用其他方法(待).......................................................................
    command = ['python', './ANN.py', arguments[2], arguments[3]]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None: break 
        if output: print(output.strip())
        sys.stdout.flush()