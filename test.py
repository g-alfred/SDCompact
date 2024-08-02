"""
File: test.py
Author: Alfredo Gonzalez
Created: 07/31/2024
Last Modified: 07/31/2024
Description: Good to use to protype new tests and architectures, also good for on-the-fly 'manual' (not really manual - you should never need to do that) runs
"""

from BTAuto.hardware.appledevice.ios import iOS, watchOS
from BTAuto.hardware.upv.upv import UPV
from .setup.devices import *
from .setup.equipment import *
from BTAuto.utils.utils import get_module_logger, toggle_console_logging, log_during_sleep
import time, os
from BTAuto.utils.files import *

# logging = get_module_logger('test', 'test.log')
# toggle_console_logging(logging, False)
# ip, port = getUPV()
# upv = UPV(ipAddress=ip, port=port, test='peaq', logger=logging)
# upv.initControlSocketwithIP()
# print('UPV initialized')

# upv.setupA2DP()
# upv.OTTRun_Start()

udid, name = getLegacy()
device = iOS(udid, name)
# device.playMusic()
# toggle_console_logging(logging, True)
# results = upv.OTTRun_MonitorAndGetResults_A2DP()
# print(results)

udid, name = getWatch()
watch = watchOS(udid, name)

device.spawnCommand()
watch.spawnCommand()

device.sendSpawnCommand('leApp')
time.sleep(1)
device.sendSpawnCommand('register p p2p high')
watch.sendSpawnCommand('leApp')
time.sleep(1)
watch.sendSpawnCommand('register p p2p high')
device.clearSpawnBuffer()
watch.clearSpawnBuffer()
for i in range(1):
    device.startBluetoothdLogging()
    device.playMusic()
    device.sendSpawnCommand('write p -f /var/mobile/'+png_file_name)
    start = time.time()
    path = os.getcwd()+'/Logs/'+str(i) 
    os.makedirs(path, exist_ok=True)
    device.saveUntilKeyword("Successfully sent data!", path+'/proxima.csv')
    watch.saveUntilKeyword("Data hash match confirmed" ,path+'/watch.csv')
    end = time.time()
    print('printing time : ')
    print(end-start)
    device.saveBluetoothdLogging(path)

    









