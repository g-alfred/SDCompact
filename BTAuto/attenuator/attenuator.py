# '''Connectivity Perf Automation Framework
#     Author: TapLabs
#     Modified By - Rahil
#     Team: Connectivity Performance and Analytics
#     Rev: 1.0.0
#     Date: October 2018
#     Copyright (c) 2018 Apple. All rights reserved
#
#     Change Log
#
# '''
# import telnetlib
# from abstract import get_module_logger
#
# NEWLINE_INDICATOR = "SCPI>"
# MIN_ATTN = 0
# MAX_ATTN = 121
#
# class Attenuator():
#
#     def __init__(self,**kwargs):
#         self.logger=kwargs.get('logger',get_module_logger(self.__class__.__name__))
#         self.ip = kwargs.get('ip',None)
#         self.port = kwargs.get('port',5024)
#         self.attn=None
#         self.tn=None
#         pass
#
#     def initConn(self):
#         self.logger.info('Estblishing Telnet connection for Attenuator at IP:{} Port:{}'.format(self.ip,self.port))
#         try:
#             self.tn = telnetlib.Telnet(self.ip,self.port)
#             self.tn.read_until(NEWLINE_INDICATOR)
#         except Exception as e:
#             self.logger.critical("Error Establishing Telnet Connection:{}".format(str(e)))
#             raise BaseException ('Error connecting to Attenuators:{}'.format(str(e)))
#         self.logger.info('Successfully Established Telnet Connection')
#
#     def close(self):
#         self.logger.info('Closing Telnet Connection to Attenuator')
#         self.tn.close()
#
#     def getAttn(self):
#         return self.attn
#
#     def setAttn(self,attn):
#         if (attn > MIN_ATTN and attn < MAX_ATTN):
#             self.logger.info('Setting Attenuation to {}'.format(attn))
#             self.tn.write("input:att {}\n".format(attn))
#             self.attn=attn
#
#
#
# if __name__ == '__main__':
#     t=Attenuator(ip='192.168.1.103',port=5024)
#     t.initConn()
#     t.close()

#!/usr/local/bin/python3
# encoding: utf-8

#
# Copyright (C) 2021 Apple Inc. All rights reserved.
#
# This file is the property of Apple Inc.
# It is considered confidential and proprietary.
#
# This file may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# Apple Inc.
#
# Author: Samraddha Dubey, Justin Park
#

import socket
import time
import logging
from .utils import NullLogger

ATTENUATOR_DEFAULT_PORT = 23
CONNECT_WAIT = 0.3
COMMAND_WAIT = 0.2


class Attenuator(object):
    MIN_ATTN = 0.0
    MAX_ATTN = 95.5

    def __init__(self, attn_ip, attn_port=ATTENUATOR_DEFAULT_PORT, att_connected=True, logger : logging = None):
        self.ip = attn_ip
        self.port = attn_port
        self.att_connected = att_connected
        self.sock = None
        self.logger = logger if logger is not None else NullLogger()
        self.sock = self._create_socket(self.ip, self.port)
        self.logger.info("Attenuator connected: %d" % self.att_connected)

    @staticmethod
    def _create_socket(ip, port):
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _sock.settimeout(10)
        _sock.connect((ip, port))
        time.sleep(CONNECT_WAIT)
        return _sock


    def process_telnet_data(self, data):
        i = 0
        length = len(data)
        result = bytearray()

        while i < length:
            byte = data[i]
            if byte == 255:  # IAC
                if i + 1 < length:
                    command = data[i + 1]
                    if command in (251, 252, 253, 254):  # WILL, WON'T, DO, DON'T
                        i += 3  # Skip command and option
                    elif command == 250:  # Start of subnegotiation
                        i += 2  # Skip IAC and SB
                        while i < length and data[i] != 240:  # IAC SE
                            i += 1
                        i += 1  # Skip SE
                    else:
                        i += 2  # Skip the command
            else:
                if byte == 13:  # Carriage return \r
                    result.append(10)  # Newline \n
                elif byte == 10:  # Newline \n
                    result.append(32)  # Space ' '
                else:
                    result.append(byte)
                i += 1

        return result.decode('utf-8', errors='ignore')


    def set_attn(self, channel, value):
        if self.att_connected:
            sock = self.sock#self._create_socket(self.ip, self.port)

            cmd = 'ATTN ' + str(channel) + ' ' + str(value)
            encode_cmd = cmd + '\r'
            sock.send(encode_cmd.encode())

            self.logger.info(cmd + ', wait: ' + str(CONNECT_WAIT + COMMAND_WAIT) + ' secs')
            time.sleep(COMMAND_WAIT)
            response = sock.recv(1081)
            decoded_response = self.process_telnet_data(response)
            self.logger.info(decoded_response)

            # sock.close()

    def set_attns(self, config_dict):
        if self.att_connected:
            for k in config_dict:
                self.set_attn(k, config_dict[k])

    def send_commands(self, cmds):
        if self.att_connected:
            sock = self.sock

            encode_cmds = cmds + '\r'
            sock.send(encode_cmds.encode())
            response = sock.recv(1081)

            self.logger.info(cmds + ', wait: ' + str(CONNECT_WAIT + COMMAND_WAIT) + ' secs')
            time.sleep(COMMAND_WAIT)
            decoded_response = self.process_telnet_data(response)
            print(decoded_response)



