import logging
import datetime
import os
from tqdm import tqdm


if not os.path.exists('logs'):
    os.makedirs('logs')
    
today = str(datetime.datetime.now()).split(" ")[0]
logging.basicConfig(filename="logs/ReachingBot-{}.log".format(today), level=logging.DEBUG, format='%(asctime)s %(message)s')

def pLog(x):
    tqdm.write(str(x))
    logging.info(x)

def jLog(x):
    logging.info(x)
