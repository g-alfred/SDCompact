"""
File: ios.py
Author: Alfredo Gonzalez
Created: 07/31/2024
Last Modified: 07/31/2024
Description: Object to access iOS & watchOS devices complete various tasks such as reading logs, pulling/pushing files, etc. 
"""
import os, sys, subprocess, pyexpat
from pycoreautomation import CAMEmbeddedDevice
import pandas as pd
import numpy as np
import pexpect, logging
from .utils import NullLogger
class iOS():
    def __init__(self, udid : str = None, name : str =None, logger : logging = None):
        self.udid = udid
        self.name = name
        self.LQM_ = 'Source_Host_LinkQualityMetrics.txt'
        self.LQM = '/var/root/'+self.LQM_
        self.TBM_ = 'Source_Tx_Beamforming_Report.txt'
        self.TBM = '/var/root/'+self.TBM_
        #enable
        self.varLQM = None
        self.varTBM = None
        self.logger = logger if logger is not None else NullLogger() 
        self.initialize()
        
    def sendRootCmd(self, command  : str):
        self.device.os().asRoot().executeCommand_arguments_withTimeout_('/bin/sh', ['-c', command],50)
        
    def _sendRootCommand(self, command : str):
        self.logger.info(self.name+" is sending root command : "+command)
        self.device.os().asRoot().executeCommand_arguments_withTimeout_('/bin/sh', ['-c', command],50)

    def _sendMobileCommand(self, command : str):
        self.device.os().asMobile().executeCommand_arguments_withTimeout_('/bin/sh', ['-c', command],50)

    def _startBluetoothProcess(self):
        self.logger.info("Starting LinkQualityReports and BeamformingReports on "+self.name)
        filename = self.LQM_
        command = 'nice -n -20 log stream --system --debug --filter \'subsystem:"com.apple.bluetooth"\' | grep LinkQualityReport >> {}'.format(filename)
        bt = self.device.os().asRoot().launchedNoHUPTaskWithCommand_arguments_('/bin/sh', ['-c', command])
        self.varLQM = {'bluetooth': dict(bt.value()).get('processIdentifier')}

        filename = self.TBM_
        command = 'nice -n -20 log stream --system --debug --filter \'subsystem:"com.apple.bluetooth"\' | grep BeamformingReport >> {}'.format(filename)
        bt = self.device.os().asRoot().launchedNoHUPTaskWithCommand_arguments_('/bin/sh', ['-c', command])
        self.varTBM = {'bluetooth': dict(bt.value()).get('processIdentifier')}

    def _stopBluetoothProcess(self):
        self.logger.info("Killing logs")
        command = 'kill -9 {}'.format(str(self.varLQM))
        self.device.os().asRoot().executeCommand_arguments_('/bin/sh', ['-c', command])

        command = 'kill -9 {}'.format(str(self.varTBM))
        self.device.os().asRoot().executeCommand_arguments_('/bin/sh', ['-c', command])

        self.device.os().asRoot().executeCommand_arguments_('/bin/sh', ['-c', 'killall log'])

    def _isDeviceConnected(self, udid : str) -> bool :  
        all_devices = CAMEmbeddedDevice.allDevices()
        for devices in all_devices:
            if udid in devices.udid():
                return True
        return False

    def install_ssh_key(self):
        """Copy the host's SSH public key to the device, so they don't require password auth
        :param device: Target device
        :type device: EmbeddedResource
        """
        device = self.device
        if device.info.is_mac:
            # .ssh file must exists because UDR
            home_dir = device.files.user_home_dir()
            dut_keyfile_path = os.path.join(home_dir, '.ssh/authorized_keys')
        else:
            dut_keyfile_path = '/var/root/.ssh/authorized_keys'
            if not device.files.exists('/var/root/.ssh', sudo=True):
                device.files.make_dir('/var/root/.ssh', sudo=True)
        temp_keyfile_path = Path(tempfile.tempdir) / \
            f'tmp_authorized_keys{uuid4()}'
        with Path('~/.ssh/id_rsa.pub').expanduser().open() as f:
            ssh_pubkey = f.read().strip('\n')
        try:
            if not device.files.exists(dut_keyfile_path, sudo=True):
                keyfile = [ssh_pubkey]
            else:
                device.copy_from(dut_keyfile_path, str(temp_keyfile_path))
                with open(temp_keyfile_path) as f:
                    keyfile = f.read().split('\n')
                    keyfile = [i for i in keyfile if i]
                if ssh_pubkey in keyfile:
                    return  # Key already exists
                else:
                    keyfile.append(ssh_pubkey)
            with open(temp_keyfile_path, 'w') as f:
                f.writelines('\n'.join(keyfile))
            device.copy_to(str(temp_keyfile_path), dut_keyfile_path, user='root')
        finally:
            # Clean up the tempfile trash
            if temp_keyfile_path.exists():
                temp_keyfile_path.unlink()

    def initialize(self):
        if self._isDeviceConnected(self.udid):
            self.device = CAMEmbeddedDevice.alloc().initWithUDID_(self.udid)
        else:
            sys.exit(self.name+' Device is not connected try : mobdev -f pair')
        self._sendRootCommand('launchctl load -w /System/Library/LaunchDaemons/rsync.plist')
        self._sendMobileCommand("defaults write com.apple.MobileBluetooth.debug HCITraces -dict StackDebugEnabled TRUE UnlimitedHCIFileSize TRUE")
        self._sendMobileCommand("defaults write com.apple.MobileBluetooth.debug Magnet -dict DisableClassic TRUE")
        self.logger.info("Device "+self.name+" successfully initialized")

    def enableLinkQualityMetrics(self):
        command = 'rm '+self.LQM
        self._sendRootCommand(command=command)
        command = 'rm '+self.TBM
        self._sendRootCommand(command=command)
        self._startBluetoothProcess()
        
    def getLogs(self, source : str = None, output : str = None):
        self.logger.info("Getting logs from "+self.name)
        if source is None:
            source = self.LQM
        rsyncString = "rsync -Kav root@"+self.name+":" + source + " " + output
        t = subprocess.check_output(rsyncString, shell=True)
        self.logger.info(t)

        if source is self.LQM:
            source = self.TBM
            rsyncString = "rsync -Kav root@"+self.name+":" + source + " " + output
            t = subprocess.check_output(rsyncString, shell=True)
            self.logger.info(t)

        self._stopBluetoothProcess()

    def playMusic(self):
        fileURLPath = '/var/mobile/PEAQ_Ref.wav'
        volume = 0.68
        # command = '/usr/local/bin/figplayAV -avaudioplayer play {} -volume {} -loopone'.format(fileURLPath, volume)
        command = 'qplay {} --volume {}'.format(fileURLPath, volume)
        self._sendRootCommand(command)
        # if self.device.os().directoryExistsAtPath_(fileURLPath).value():
        #     self.device.os().launchedNoHUPTaskWithCommand_arguments_('/bin/sh', ['-c', command])
        # else:
        #     self.device.rsyncFromLocal_toRemote_options_('PEAQ_Ref.wav', '/var/mobile', "-a -v")
        #     self.device.os().launchedNoHUPTaskWithCommand_arguments_('/bin/sh', ['-c', command])

    def stopMusic(self):
        self.device.os().asRoot().executeCommand_arguments_('/bin/sh', ['-c', "killall figplayAV"])

    def callNumber(self):
        number = '9548042624'
        self.device.coreTelephony().callNumber_waitForAnswer_(number, False)

    def faceTimeAudio(self, address):
        waitForActive = False
        timeout = 10
        self.device.faceTime().faceTimeAudioWithAddress_waitForActive_withTimeout_(address,waitForActive,timeout)

    def transferFiletoDevice(self, LocalfilePath : str, RemoteFilePath : str) -> None:
        self.logger.info('scp '+LocalfilePath+' root@'+self.name+':'+RemoteFilePath)
        os.system('scp '+LocalfilePath+' root@'+self.name+':'+RemoteFilePath)

    def transferFiletoHost(self, PathOnDevice : str, PathOnLocal : str) -> None:
        self.logger.info('scp root@'+self.name+':'+PathOnDevice+' '+PathOnLocal)
        os.system('scp root@'+self.name+':'+PathOnDevice+' '+PathOnLocal)

    def leApp(self, command):
        pass

    def message(self):
        #not sure if this works 
        self.device.iMessage('9548042624')

    def spawnCommand(self) -> None:
        self.logger.info('Spawning child for '+self.name)
        ssh_command = 'ssh root@'+self.name
        child = pexpect.spawn(ssh_command, encoding='utf-8')
        self.spawn = child
        
    def sendSpawnCommand(self, command : str) -> None:
        self.logger.info('Sending spawn command '+command+" to "+ self.name)
        self.spawn.sendline(command)
        self.spawn.expect_exact(command)  # Expect the command to be echoed back
        self.spawn.expect(pexpect.TIMEOUT, timeout=3)  # Wait for the command to execute
        output = self.spawn.before.strip()
        return output
    
    def readSpawnBefore(self) -> str:
        return self.spawn.before
    
    def readSpawnAfter(self) -> str:
        return self.spawn.after
    
    def saveSpawnBefore(self, path : str ) -> None:
        output = self.readSpawnBefore
        df = pd.DataFrame([output], columns=['leApp'])
        df.to_csv(path, index=False)
        self.logger.info("for "+self.name+" got spawn out")
        self.logger.info(output)
    
    def readUntilKeyword(self, keyword : str, buffer_size : int =1024*1024, timeout : int =3) -> str:
        """Reads all output from the device until the keyword is found."""
        output = ""
        try:
            while True:
                # Read non-blocking to get all output until keyword is found
                chunk = self.spawn.read_nonblocking(size=buffer_size, timeout=timeout)
                output += chunk
                if keyword in output:
                    break
        except pexpect.EOF:
            print("SSH session closed.")
        except pexpect.exceptions.TIMEOUT:
            pass  # Continue reading if timeout occurs
        self.logger.info("for "+self.name+" got spawn out")
        self.logger.info(output)
        return output

    def saveUntilKeyword(self, keyword : str, path : str) -> None:
        output = self.readUntilKeyword(keyword)
        df = pd.DataFrame([output], columns=['leApp'])
        df.to_csv(path, index=False)


    def clearSpawnBuffer(self):
        """Reads and discards any existing output in the spawn buffer."""
        self.logger.info("Clearing spawn buffer for "+self.name)
        try:
            while True:
                self.spawn.read_nonblocking(size=1024*1024, timeout=1)
        except pexpect.exceptions.TIMEOUT:
            pass  # Ignore timeouts since it means the buffer is cleared
        except pexpect.EOF:
            print("SSH session closed.")

    def readSpawnOutput(self) -> str:
        try:
            output = self.spawn.read_nonblocking(size=1024*1024, timeout=1)  
        except pexpect.EOF:
            print("SSH session closed.")
            output = self.spawn.before
        except pexpect.exceptions.TIMEOUT:
            print('timeout occured , printing before')
            output = self.spawn.before
        self.logger.info("Reading output for "+self.name)
        self.logger.info(output)
        return output
        
    
    def saveSpawnOutput(self, path) -> None:
        output = self.readSpawnOutput()
        df = pd.DataFrame([output], columns=['leApp'])
        df.to_csv(path, index=False)
    
    def startBluetoothdLogging(self, filename : str = None) -> None:
        if filename is None:
            filename = 'file.txt'
        self.bluetoothd_filename = filename
        self._sendRootCommand('rm '+filename)
        command =  "log stream --level debug --style compact --predicate 'process == \"bluetoothd\"' > {}".format(filename)
        self.sendRootCmd(command=command)

    def saveBluetoothdLogging(self, path : str) -> None:
        self.transferFiletoHost('/var/root/'+self.bluetoothd_filename, path)

    def isWifiConnected(self):
        pass

    def isCellularConnected(self):
        pass


class watchOS(iOS):
    def __init__(self, udid: str = None, name: str = None):
        super().__init__(udid, name)