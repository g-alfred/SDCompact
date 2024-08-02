import re, subprocess
import pandas as pd
import numpy as np
import re
from typing import Tuple, List, Union, Tuple
import sys, time
import os
import plistlib, logging
from datetime import datetime

def remove_non_numeric(s: List[str], returnInt = True) -> List[Union[int, str]]:
    n = [re.sub(r'[^0-9]', '', temp) for temp in s]
    if returnInt:
        n = np.array(n).astype(int)
    else:
        n = np.array(n)
    return n

def save_or_merge_file(file_path : str, data : pd.Series, filename : str) -> None:
        os.makedirs(file_path, exist_ok=True)
        file_path = file_path + filename
        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            data_df = data.to_frame()
            combined_data = pd.concat([existing_data, data_df], ignore_index=True)
            combined_data.to_csv(file_path, index=False)
        else:
            # Save the Series to a new CSV file
            data.to_csv(file_path, index=False)

def find_all_occurrences(self, char, string) -> List[str]:
    return [i for i, c in enumerate(string) if c == char]

def list_folders(directory: str) -> List[str]:
    return [item for item in os.listdir(directory) if os.path.isdir(os.path.join(directory, item))]

def is_all_nan_or_empty(arr: np.ndarray) -> bool:
            if arr.size == 0:
                return True
            return np.all(np.isnan(arr))

def log_during_sleep(total_sleep_time, log_interval):
    start_time = time.time()
    end_time = start_time + total_sleep_time
    while time.time() < end_time:
        print("Collecting Data...")
        time.sleep(log_interval)

def convert_bita(file_path):
    firmware_log_gz_filename = os.path.splitext(file_path)[0] + '.gz'
    firmware_log_unzipped_filename = os.path.splitext(file_path)[0]
    firmware_log_csv_filename = os.path.splitext(file_path)[0] + '.csv'
    fw_log_cmds = [
        '/bin/cp "{}" "{}"'.format(file_path, firmware_log_gz_filename),
        '/usr/bin/gunzip "{}"'.format(firmware_log_gz_filename),
        '/bin/mv "{}" "{}"'.format(firmware_log_unzipped_filename, firmware_log_csv_filename)
    ]
    for cmd in fw_log_cmds:
        subprocess.call(cmd, shell=True)
    return firmware_log_csv_filename

class PropertyManager():
    def __init__(self,**kwargs):
        self.path = kwargs.get('path',None)
        self.config =self._readPlist()
        pass
    @classmethod
    def loadConfigFile(cls,path):
        t = PropertyManager(path=path)
        return t.config

    def _readPlist(self):

        with open(self.path, 'rb') as fp:
            ret = plistlib.loads(fp.read())
        return ret
        # return plistlib.readPlist(self.path)

    def _writePlist(self):
        pass

def getDateTime():
    return datetime.now().strftime('%m-%d_%H-%M-%S')


ConlogName=os.path.join(os.path.dirname(__file__),"Logs", "Console_{}.log".format(getDateTime()))
if not os.path.isdir(os.path.join(os.path.dirname(__file__),"Logs")):
    os.mkdir(os.path.join(os.path.dirname(__file__),"Logs"))

def get_module_logger(mod_name : str,filename : str = ConlogName ) -> logging.getLogger:
    ConlogName = filename
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    filehandler=logging.FileHandler(filename,"a+")
    formatter = logging.Formatter(
            '%(asctime)s %(module)-12s %(funcName)-20s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    filehandler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(filehandler)
    logger.setLevel(logging.DEBUG)
    return logger

class NullLogger:
    def info(self, msg, *args, **kwargs):
        pass  # Do nothing

    def warning(self, msg, *args, **kwargs):
        pass  # Do nothing

    def error(self, msg, *args, **kwargs):
        pass  # Do nothing

    def debug(self, msg, *args, **kwargs):
        pass  # Do nothing

    def critical(self, msg, *args, **kwargs):
        pass  # Do nothing
    
from functools import wraps
import errno
import os
import signal

