"""
Last Edited : Alfredo Gonzalez 
    Date: 07/31/2024
"""


import sys, os
import numpy as np
import pandas as pd
from .attenuator.attenuator import Attenuator
from .appledevice.ios import iOS
from .upv.upv import UPV
from aci.api import Logger
from .utils.devices import *
from .utils.phone_number import phone_number
from .utils.utils import log_during_sleep, NullLogger
from .sniffer.EllisysSniffer import EllisysSniffer
import logging



class AWGN():
    def __init__(self, sniffer : EllisysSniffer, attenuator : Attenuator, bitacorra :Logger, device : iOS, output : str = None, legacy : bool = False, logger : logging = None) -> None:
        self.sniffer = sniffer
        self.attenuator = attenuator
        self.bitacorra = bitacorra
        self.device = device
        if output is None:
            output = os.getcwd()+'/currentLogs'
        self.output = output
        self.legacy = legacy
        self.waitForTest = False
        self.results = {
            'right' : [],
            'left'  : [],
            'stereo': [] 
            }
        self.logger = logger if logger is not None else NullLogger()

    def _alert(self):
        udid, name = getFarrend()
        phone = phone_number()
        if phone is not None:
            device = iOS(udid, name)
            device.faceTimeAudio(phone)

    def _make_path(self, this_attenuation_value : int, iterate : int) -> None:
        this_path = self.output+'/'+str(this_attenuation_value)+'dB/iteration_'+str(iterate)
        os.makedirs(this_path, exist_ok=True)
        self.output_path = this_path

    def _start_equipment(self, this_attenuation_value : int, iterate : int, attenuation_offset : int):
        self.logger.info("Starting attenuation point "+str(this_attenuation_value))
        self.logger.info("Starting this iteration "+str(iterate))

        self.attenuator.set_attn(1, this_attenuation_value)
        self.attenuator.set_attn(2, this_attenuation_value+attenuation_offset)

        self.logger.info('Start Sniffer Logs')
        self.sniffer.startRecordingWithAttempts()

        self.logger.info('Start bitacorra logs')
        self.bitacorra.start_session(clear_logs=True, dump=True)

    def _start_devices(self):
        self.logger.info('Play Music')
        if self.legacy:
            self.device.enableLinkQualityMetrics()
        self.device.playMusic()

    def _collect_equipment(self, this_attenuation_value : int, iterate : int) -> None:
        this_path = self.output_path

        self.logger.info('Saving Logs')
        self.logger.info('Saving Sniffer Logs')
        _tempTracePath = self.sniffer.stopRecording('C:\Shared\RemoteCaptures')
        self.sniffer.closeTraceFile()
        temp_sniffer_paths = {
            'TraceFilePath': [_tempTracePath],
        }
        pd_temp = pd.DataFrame(temp_sniffer_paths)
        pd_temp.to_csv(this_path+'/snifferFileLocation.csv')

        self.logger.info('Save Bitacorra Logs')
        self.bitacorra.save_session(folder_path=this_path, filename_prefix='Bitacorra')

    def _collect_devices(self, this_attenuation_value : int, iterate : int) -> None:
        this_path = self.output_path

        self.device.stopMusic()
        if self.legacy:
            self.device.getLogs(output=this_path)

    def waitForTestToFinish(self, delay : int, log_interval : int):
        """
        Call this function before starting test if you want a delay between starting the test and collecting data
        ->customly made for cases where the UPV isn't being used

        delay : How long of a delay 
        log_interval : How often do you want logs outputted during delay 
        """
        self.waitForTest = True
        self.logNumbers = [ delay, log_interval]

    def _action_during_test(self):
        log_during_sleep(self.logNumbers[0], self.logNumbers[1])

    def test(self, attenuation_values : np.ndarray, numberOfIterations : int , attenuation_offset : int = None) -> None:
        if attenuation_offset is None:
            attenuation_offset = 0
    
        for this_attenuation_value in attenuation_values:
            for iterate in range(numberOfIterations):
                self._make_path(this_attenuation_value, iterate)
                self._start_equipment(this_attenuation_value, iterate, attenuation_offset)
                self._start_devices()
                if self.waitForTest:
                    self._action_during_test()
                self._collect_equipment(this_attenuation_value, iterate)
                self._collect_devices(this_attenuation_value, iterate)
        self._alert()

class A2DP(AWGN):
    def __init__(self, sniffer: EllisysSniffer, attenuator: Attenuator, bitacorra: Logger, device: iOS, output: str = None, legacy: bool = False, upv : UPV = None) -> None:
        super().__init__(sniffer, attenuator, bitacorra, device, output, legacy)
        self.upv = upv

    def _start_equipment(self, this_attenuation_value : int, iterate : int, attenuation_offset : int):
        super()._start_equipment(this_attenuation_value, iterate, attenuation_offset)
        self.upv.setupA2DP()
        self.upv.OTTRun_Start()
        
    def _collect_equipment(self, this_attenuation_value : int, iterate : int) -> None:
        this_path = self.output_path

        this_result = self.upv.OTTRun_MonitorAndGetResults_A2DP()
        self.results['right'].append(float(this_result[0]))
        self.results['left'].append(float(this_result[1]))
        self.results['stereo'].append(float(this_result[2]))
        df = pd.DataFrame(self.results)
        df.to_csv(this_path+'/UPV_Scores.csv')
        self.results['right'] = []
        self.results['left'] = []
        self.results['stereo'] = []

        super()._collect_equipment(this_attenuation_value, iterate)
        
            
class HFP(AWGN):
    def _start_equipment(self, this_attenuation_value : int, iterate : int, attenuation_offset : int):
        if self.upv is None:
            super()._start_equipment(this_attenuation_value, iterate, attenuation_offset)
        else:
            pass #implement UPV

    def _collect_equipment(self, this_attenuation_value : int, iterate : int) -> None:
        if self.upv is None:
            super()._collect_equipment(this_attenuation_value, iterate)
        else:
            pass #implement UPV







                

