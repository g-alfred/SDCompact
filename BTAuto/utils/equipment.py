from typing import Tuple

def getAttenuator() -> str:
    return '192.168.1.10'

def getSniffer() -> Tuple[str, str]:
    ip = '192.168.1.20'
    port = '12345'
    return ip, port

def getUPV() -> Tuple[str, int]:
    ip = '192.168.1.80'
    port = 5025
    return ip, port