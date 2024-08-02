'''
Author :taplabs
Date:4/29/16 5:08 PM


This is just an inheritance file from the legacy scripts
'''

import socket,sys,os,shutil, subprocess
import ftplib
from datetime import datetime
from ftplib import *

import re,time
import sys, os
import numpy as np
import pandas as pd
import signal
from .utils import PropertyManager, NullLogger
from aci.api import Logger
import logging
from . import OTT



RE_SND_MSG= re.compile(r'#\w+#')

class TimeoutError(Exception):
    pass

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

class UPV():

    MAX_UPV_SOCKET_ATTMPTS = 3
    CFG =PropertyManager.loadConfigFile(path=os.path.join(os.getcwd(), 'SDCompact/BTAuto/upv/ConfigList.plist'))

    def __init__(self, logger : logging = None  , ipAddress : int = None, port : str = None, test : str = None, **kwargs):
        self.logger = logger if logger is None else NullLogger()
        self.ipAddress = ipAddress
        self.port = port
        self.cfgType=test
        self.vars=kwargs.get('vars',None) # Holds Extra information like upv_gain ,rx_gain ,etc
        self.sock=None
        self.sockr=None
        self.fsock=None
        

    @classmethod
    def initwithIP(cls,**kwargs):
        t=UPV(**kwargs)
        t.initControlSocketwithIP()
        return t
    #-------------------------- Control Socket----------------------------------------#
    def initControlSocketwithIP(self):
        # self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock = socket.socket()
        print('Establishing UPV Socket at IP:{}  Port:{} Socket:{}'.format(self.ipAddress,self.port,self.sock))
        try:
            self.sock.connect((self.ipAddress,self.port))
        except socket.error as e:
            print('Failed to Establish Socket ,Error:{}, Attempts Left {}'.format(str(e),UPV.MAX_UPV_SOCKET_ATTMPTS))
            UPV.MAX_UPV_SOCKET_ATTMPTS -= 1
            while(UPV.MAX_UPV_SOCKET_ATTMPTS >0):
                self.initControlSocketwithIP()
            
            self.logger.error('Cant Establish UPV Connection')
            sys.exit()
        self.logger.info('Successfully Established UPV Socket @{}:{} '.format(self.ipAddress, self.port))
        # import pdb;
        # pdb.set_trace()
        pass

    def sendMsg(self,msg):
        msg = self.subMsg(msg)
        self.logger.info('{} ->Sending Message :{}'.format(self.__class__.__name__,msg))
        try:
            self.sock.sendall((msg+"\n").encode('utf-8'))
        except socket.error:
            self.logger.info("UPV Socket Broken.Trying one more time")
            self.initControlSocketwithIP()
            raise RuntimeError ('{} Socket Broken'.format(self.__class__.__name__))

    def revMsg(self,delay=0.0):
        # import pdb;
        # pdb.set_trace()
        time.sleep(delay)
        recv=''
        try:
            recv=self.sock.recv(1024)
        except socket.error as e:
            pass
        #self.logger.info('{} <-Receiving Message :{}'.format(self.__class__.__name__,recv.strip("\n")))
        #self.logger.info(('{} <-Receiving Message :{}'.format(self.__class__.__name__, recv.strip("\n")))).encode('utf-8')
        # return recv
        return recv.decode('utf-8')

    def waitForOPC_getValue(self):
        self.sendMsg("*OPC?")
        while(True):
            rcv= self.revMsg()
            self.logger.info("\t\tRecevied Message:{}".format(rcv))
            if rcv:
                return rcv

    def waitforReply(self):
        while(True):
            recv = self.revMsg()
            if recv:
                self.logger.debug("\t\tRecevied Message:{}".format(recv))
                return recv


    def closeControlSocket(self):
        self.logger.info('Closing Socket'.format(self.sock))
        self.sock.close()

    def subMsg(self,msg):
        ms1=msg
        matches = re.findall(RE_SND_MSG,msg)
        for match in matches:
            msg=re.sub(match,getattr(self.vars,str(match).strip('#')),msg)
        if matches:
            self.logger.info('{} --> {}'.format(ms1,msg))
        return msg


    #-------------------------- FTP Connection ------------------------------------#
    def initFTPConn(self):
        self.logger.info('Establishing FTP Socket :{} at IP:{}'.format(self.fsock,self.ipAddress))
        self.fsock = FTP()
        try:
            self.fsock.connect(self.ipAddress,21)
            self.logger.info('Logging in via FTP')
            self.fsock.login("OTT","OTT") # Hard Coded
        except ftplib.all_errors:
            self.logger.critical('Login Failed :{}'.format(ftplib.error_reply))
            exit(1)

    def getFile(self,url,binary=True):
        self.logger.info('Getting  File from UPV:{} binarymode {}'.format(url,binary))
        if binary:
            self.fsock.retrbinary('RETR {}'.format(str(url)),open(url,'wb').write)
        else:
            self.fsock.retrlines('RETR {}'.format(str(url)),open(url,'wb').write)


    def getFile_deleteandMove(self,url,destination,binary=True):# Transfers File and Moves

        self.logger.info('Getting File from UPV:{} -> Destination:{} binarymode {}'.format(url,destination,binary))
        try:
            self.initFTPConn()
            if binary:
                self.fsock.retrbinary('RETR {}'.format(str(url)),open(url,'wb').write)
            else:
                self.fsock.retrlines('RETR {}'.format(str(url)),open(url,'wb').write)
            self.fsock.delete(url)
            shutil.move(url,destination)
            self.closeFTP()
        except ftplib.all_errors as e:
            self.logger.warning('Encountered FTP Error:{}'.format(str(e)))
        except Exception as e:
            self.logger.warning('Encountered Exception:{}'.format(str(e)))
            pass

    def downloadAllFilesAndDelete(self,source,destination):
        self.logger.info('Getting File from UPV:{} -> Destination:{} binarymode {}'.format(source, destination,True))
        try:
            self.initFTPConn()
            os.makedirs(destination)
            #self.fsock.cwd(source)

            flist =self.fsock.nlst()

            for file in flist:
                self.logger.info("Copying file from UPV:"+file)
                self.fsock.retrbinary('RETR {}'.format(str(file)), open(file, 'wb').write)

                #self.fsock.retrlines('RETR {}'.format(str(url)), open(url, 'wb').write)
                p = source+"\\"+file
                self.fsock.delete(file)
                shutil.move(file, destination)
            #self.closeFTP()
        except ftplib.all_errors as e:
            self.logger.warning('Encountered FTP Error:{}'.format(str(e)))
        except Exception as e:
            self.logger.warning('Encountered Exception:{}'.format(str(e)))
            pass
        self.logger.info('Closing FTP Socket to UPV')
        self.fsock.close()

    #-------------------------- UPV Configuration ---------------------------------#
    def configureUPV(self,cfgType=None):
        if not cfgType:
            if self.cfgType:
                cfgType=self.cfgType
        self.logger.info('UPV Configuration:{}'.format(cfgType))

        #Choosing Configuration
        if cfgType == 'polqa':cfg=UPV.CFG.UPV.POLQA
        elif cfgType == 'peaq':cfg=UPV.CFG.UPV.PEAQ
        else: return

        query_cmd = cfg.QueryCommand
        # Generator Config
        GeneratorCfgreceive_msgs=[]
        for command in cfg.GeneratorConfig:
            self.sendMsg(command)
            #self.sendMsg(query_cmd)
            GeneratorCfgreceive_msgs.append(self.waitForOPC_getValue())

        # Generator Function
        GeneratorFunctionRcvMsgs=[]
        for command in cfg.GeneratorFunction:
            self.sendMsg(command)
            #self.sendMsg(query_cmd)
            GeneratorFunctionRcvMsgs.append(self.waitForOPC_getValue())

        #Analyzer Config
        AnalyzerCfgMsgs=[]
        for command in cfg.AnalyzerConfig:
            self.sendMsg(command)
            #self.sendMsg(query_cmd)
            AnalyzerCfgMsgs.append(self.waitForOPC_getValue())

        #Analyzer Function
        AnalyzerFcnMsgs=[]
        for command in cfg.AnalyzerFunction:
            self.sendMsg(command)
            #self.sendMsg(query_cmd)
            AnalyzerFcnMsgs.append(self.waitForOPC_getValue())

        #Ready for Test

        for command in cfg.ReadyTest:
            self.sendMsg(command)
            self.waitForOPC_getValue()

    #-------------------------- UPV Configuration ---------------------------------#

    def runPEAQTest(self):
        cmd= UPV.CFG.UPV.PEAQ.Command
        query=UPV.CFG.UPV.PEAQ.QueryCommand
        # Init
        # self.sendMsg(cmd.init)
        # self.waitForOPC_getValue()
        # Sense on channel 1

        self.sendMsg(cmd.sense1)
        self.waitforReply()
        #Sense on Channel 2
        self.sendMsg(cmd.sense2)
        self.waitforReply()
        # Get Delay Detect
        self.sendMsg(cmd.delayDetect)
        DelayDetect=self.waitforReply()
        #Get PEAQ
        self.sendMsg(cmd.getScore)
        odg=self.waitforReply()
        # Save Wave File
        self.sendMsg(cmd.save)
        self.sendMsg(query)
        self.waitforReply()
        #Get Distortion Index
        self.sendMsg(cmd.getDistortionIndex)
        di=self.waitforReply()
        #Get Delay Metric
        self.sendMsg(cmd.getDelayMetric)
        Delay=self.waitforReply()
        report={'DelayDetect':re.sub('[a-zA-Z]','',DelayDetect.strip()),
                'odg':odg.strip(),
                'di':di.strip(),
                'Delay':re.sub('[a-zA-Z]','',Delay.strip())}
        return report


    def runPOLQATest(self):
        cmd= UPV.CFG.UPV.POLQA.Command
        query=UPV.CFG.UPV.POLQA.QueryCommand
        # Set Ouput On
        self.sendMsg(cmd.outputOn)
        self.sendMsg(query)
        self.revMsg()
        # setOutputChannel
        self.sendMsg(cmd.setOutputChannel)
        self.sendMsg(query)
        self.revMsg()
        # Save Wave file
        self.sendMsg(cmd.save)
        self.sendMsg(query)
        self.revMsg()
        # Init
        self.sendMsg(cmd.init)
        self.sendMsg(query)
        self.revMsg()
        #Get POLQA
        self.sendMsg(cmd.getPOLQA)
        self.revMsg()
        #Get Average Delay
        self.sendMsg(cmd.getAvgDelay)
        self.revMsg()
        #Get Atteuation
        self.sendMsg(cmd.getAttenuation)
        self.revMsg()

    ################ FROM OTT TEST #############################

    def OTT_sendbuffcommands(self,buff_strings=[]):
        for i in range(len(buff_strings)):
            self.sendMsg('SYSTem:MEMory:STRing{} "{}"\n'.format(i + 1, buff_strings[i]))
        return

    def OTTRun_Configure(self):
        self.sendMsg('STAT:OPER:NTR 16384')
        self.sendMsg('STAT:OPER:ENAB 16384')
        self.sendMsg('*SRE 128')
        self.waitForOPC_getValue()

    def OTTRun_Start(self):
        self.logger.error("Running OTTRun_kill")
        self.OTTRun_kill()
        self.logger.error("Running OTTRun_Configure")
        self.OTTRun_Configure()
        self.logger.error("Running OfflineTestTool.exe")
        self.sendMsg("SYSTem:PROG:EXEC 'C:\\Program Files\\Rohde&Schwarz\\R&S Offline Test Tool\\OfflineTestTool.exe'")
        return self.waitForOPC_getValue()


    def OTTRun_Monitor(self,default_timeout=300):
        self.logger.info("UPV monitoring test run...")
        ts=datetime.now().strftime('%s')
        rcvMsg = None
        string_hold = []
        try:
            with timeout(seconds=default_timeout):
                while (1):
                    self.sendMsg('SYSTem:MEMory:STRing102?')
                    rcvMsg = self.revMsg()
                    rcvMsg=rcvMsg.replace("\n","")
                    string_hold.append((rcvMsg))
                    if 'running' in rcvMsg:
                        self.logger.info('UPV Testing On-Going')
                    #self.logger.debug("OTTRUNMonitor:"+rcvMsg)
                    if 'completed' in rcvMsg:
                        self.logger.info("UPV test iteration is completed...")
                        break
                    if 'timeout' in rcvMsg:
                        self.logger.warning("UPV might have timed out")
                        print('UPV went to caca , restarting script :) GOOD LUCK! ')
                        subprocess.Popen([sys.executable] + sys.argv)
                        sys.exit()
                    if 'empty' in rcvMsg:
                        self.logger.warning('Messages from UPV are empty - Might not be working')
                    time.sleep(20)
                self.sendMsg("SYSTem:MEMory:STRing104?")
                error=self.revMsg()
                print(error)
                #error.replace("\n", "")
        except TimeoutError:
            print('Time out - Could be UPV issue or just a trigger fail')
            print(string_hold)
            self.OTTRun_kill() #killing the whole program when trigger fails is not the best idea
            # rcvMsg = 'timeout'
            return (rcvMsg)

        return (rcvMsg,error,ts,datetime.now().strftime('%s'))

    def OTTRun_kill(self):
        self.sendMsg("SYSTem:PROG:EXEC 'D:\\UPV\\OfflineTestTool\\kill_OTT.exe'")
        return self.waitForOPC_getValue()

    def OTT_ReadBuffer(self):
        in_buff =[]
        for i in range(101,144):
            self.sendMsg("SYSTem:MEMory:STRing{}?".format(i))
            rcv=self.revMsg()
            if(len(rcv)>0 and "\n" in rcv):
                rcv=rcv.replace("\n", "")

            in_buff.append(rcv)
        return in_buff

    def OTTRun_MonitorAndGetResults_A2DP(self, default_timeout=300):
        recievemsg=self.OTTRun_Monitor(default_timeout)
        print('OTTRun Monitor did not timeout , yay!')
        scores=[]
        if(recievemsg[0] =="completed"):
            result =self.OTT_ReadBuffer()
            print('Read Buffer of UPV')
            # self.logger.info(result)
            # self.logger.info("ODGLeft:"+result[4])
            # scores.append(result[4])
            # self.logger.info("ODGRight:" + result[5])
            # scores.append(result[5])
            # self.logger.info("ODGStereo:"+result[6])
            self.logger.info(result)
            if result[4] != 'empty':
                self.logger.info("ODGLeft:"+result[4])
            else:
                result[4] = 1.00
            scores.append(result[4])
            if result[5] != 'empty':
                self.logger.info("ODGRight:" + result[5])
            else:
                result[5] = 1.00
            scores.append(result[5])
            if result[6] != 'empty':
                self.logger.info("ODGStereo:" + result[6])
            else:
                result[6] = 1.00
            scores.append(result[6])
            scores.append(result[1])
            scores.append(result[2])
            return scores
        elif(recievemsg[0] =='timeout'):
            self.logger.info("Test Iteration Failed:Timeout")
            return scores.append('timeout')
        elif recievemsg[0] == 'waiting for trigger':
            self.logger.info('Trigger did not activate')
            return scores.append('trigger failure')
        else:
            raise Exception("UPV Failure:"+recievemsg)

    def OTTRun_MonitorAndGetResults_HFP(self, default_timeout=300):
        recievemsg=self.OTTRun_Monitor(default_timeout)
        scores=[]
        if(recievemsg[0] =="completed"):
            result =self.OTT_ReadBuffer()
            self.logger.info(result)
            self.logger.info("POLQA Left:"+result[4])
            scores.append(result[4])
            self.logger.info("POLQA Right:" + result[5])
            scores.append(result[5])

            scores.append(result[1])
            scores.append(result[2])

            self.logger.info("Attenuation Left:" + result[26])
            self.logger.info("Attenuation Right:" + result[27])
            scores.append(result[26])
            scores.append(result[27])
            return scores
        elif(recievemsg[0] =='timeout'):
            self.logger.info("Test Iteration Failed:Timeout")
            return scores.append('timeout')
        else:
            raise Exception("UPV Failure:"+recievemsg)


# easier API functions here 


    def setupA2DP(self):
        try:
            self.OTT_sendbuffcommands(OTT.peaq_buff_strings)
        except:
            self.logger.ERROR('The PEAQ commands could not be sent ')

    def setupHFP(self):
        try:
            self.OTT_sendbuffcommands(OTT.polqa_buff_strings)
        except:
            self.logger.ERROR('The POLQA command cant be sent')

    def processA2DPResults(self, currentscores):
        if (len(currentscores) > 0):
            if (currentscores[0] == "timeout"):
                self.logger.info("AudioQuality RUN Failed:Timeout")
                return False
            self.results.odgLeft.append(currentscores[0])
            self.results.odgRight.append(currentscores[1])
            self.results.odgStereo.append(currentscores[2])
            self.results.timestamp.append(currentscores[4])
            self.results.status.append(currentscores[3])
            return True

        else:
            return False

    def processHFPResults(self, currentscores):
        if (len(currentscores) > 0):
            if (currentscores[0] == "timeout"):
                self.logger.info("AudioQuality RUN Failed:Timeout")
                return False
            self.results.polqaLeft.append(currentscores[0])
            self.results.polqaRight.append(currentscores[1])
            self.results.timestamp.append(currentscores[3])
            self.results.status.append(currentscores[2])
            self.results.attnLeft.append(currentscores[4])
            self.results.attnRight.append(currentscores[5])
            return True
        else:
            return False
        
        
        
# if __name__ == '__main__':

#     t=UPV(ip='192.168.1.20',port=5025,cfgType='peaq')
#     #t.initControlSocketwithIP()

#     t.downloadAllFilesAndDelete("d:\\UPV\OfflineTestTool\Degraded\\","/Users/cpaimac/Automation/LuchosLabAutomation-Anite/Logs/A2DP/A2DP_BitRate_Threshold_50_70_SNR40_10-09_15-54-20/Measurement/peafiles")
#     #t.initFTPConn()
#     #t.getFile_deleteandMove('PEAQ_TEMP.wav','../Logs/')


