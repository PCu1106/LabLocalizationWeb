
import time
import logging
import sys
a='101'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.debug(a)
print(str(a))
print(int('5.0'))
for i in range(5):
    print(i)
    #time.sleep(1)

'''
from random import *
import time
for i in range(5):
    print("showRandomWithSleep.py")
    print(random())
    time.sleep(random()*5)
 '''