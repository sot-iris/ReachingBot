import logging
import datetime
from tqdm import tqdm

today = str(datetime.datetime.now()).split(" ")[0]
logging.basicConfig(filename="ReachingBot-{}.log".format(today), level=logging.DEBUG, format='%(asctime)s %(message)s')

def pLog(x):
    tqdm.write(str(x))
    logging.info(x)

def jLog(x):
    logging.info(x)
