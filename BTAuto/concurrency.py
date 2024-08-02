"""
File: concurrency.py
Author: Alfredo Gonzalez
Created: 07/31/2024
Last Modified: 07/31/2024
Description: Object to access iOS & watchOS devices complete various tasks such as reading logs, pulling/pushing files, etc. 
"""
import sys, os
from .basics import A2DP
from .attenuator.attenuator import Attenuator
from .upv.upv import UPV
from .utils.files import *
from aci.api import Logger
from .appledevice.ios import iOS
import numpy as np
from .sniffer.EllisysSniffer import EllisysSniffer
import logging

class TriangleSingleSweep(A2DP):
    
    def __init__(self, sniffer: EllisysSniffer, attenuator: Attenuator, bitacorra: Logger, device: iOS, output: str = None, legacy: bool = False, upv : UPV = None , secondary_device : iOS = None) -> None:
        super().__init__(sniffer, attenuator, bitacorra, device, output, legacy, upv)
        self.secondary_device = secondary_device
        self.device.transferFiletoDevice(png_file, '/var/mobile/')

        #generating spawns for leApp control 
        self.device.spawnCommand()
        self.secondary_device.spawnCommand()

        self.secondary_device.sendSpawnCommand('leApp')
        self.device.sendSpawnCommand('leApp')
        self.logger.info('leApp initialized successfully ')

        self.secondary_device.sendSpawnCommand('register p p2p high')
        self.device.sendSpawnCommand('register p p2p high')
        print('Add a check here to make sure p2p pipe was successful ')

        self.waitForTest = True

    def _action_during_test(self):
        self.secondary_device.saveUntilKeyword("Data hash match confirmed", self.output_path)
        self.device.saveUntilKeyword("Successfully sent data!", self.output_path)
        
    def _start_devices(self):
        self.device.clearSpawnBuffer()
        self.secondary_device.clearSpawnBuffer()

        self.device.startBluetoothdLogging()
        self.device.sendSpawnCommand('write p -f /var/mobile/'+png_file_name)
        if "Couldn't open file" in self.device.readSpawnBefore():
            sys.exit("Somthing is wrong, file is not in device ")
        super()._start_devices()

    def _collect_devices(self, this_attenuation_value : int, iterate : int) -> None:

        this_path = self.output_path

        self.device.saveSpawnBefore(this_path+'/source.csv')
        self.device.saveSpawnBefore(this_path+'/sink.csv')
        self.device.transferFiletoHost('var/root/'+png_file_name, this_path)

        self.device.stopMusic()
        if self.legacy:
            self.device.getLogs(output=this_path)

class TriangleDoubleSweep(TriangleSingleSweep):
    
    def _start_equipment(self, this_attenuation_value : int, iterate : int, attenuation_offset : int):
        self.logger.info("Starting attenuation point "+str(this_attenuation_value))
        self.logger.info("Starting this iteration "+str(iterate))

        self.attenuator.set_attn(1, this_attenuation_value)
        self.attenuator.set_attn(2, this_attenuation_value+attenuation_offset)
        self.attenuator.set_attn(5, this_attenuation_value)

        self.logger.info('Start Sniffer Logs')
        self.sniffer.startRecordingWithAttempts()

        self.logger.info('Start bitacorra logs')
        self.bitacorra.start_session(clear_logs=True, dump=True)



