from BTAuto.utils.utils import *
from BTAuto.appledevice.ios import iOS, watchOS
from BTAuto.attenuator.attenuator import Attenuator
from BTAuto.sniffer.EllisysSniffer import EllisysSniffer
from BTAuto.upv.upv import UPV
from BTAuto.concurrency import TriangleSingleSweep
from aci.api import Logger
import numpy as np
from setup.devices import *
from setup.equipment import *


FILENAME = "A2DP"
PATHNAME = os.getcwd()+"/Logs/Legacy/AWGN"
logger = get_module_logger_old(FILENAME, "HostLogHold")

def set_up_equipment():
    ip = getAttenuator()
    attenuator = Attenuator(ip, logger=logger)

    ip, port = getUPV()
    upv = UPV(logger, ip, port, 'peaq')

    ip, port = getSniffer()
    sniffer = EllisysSniffer(ip, port)

    return attenuator, upv, sniffer

def set_up_devices():
    ip, name = getLegacy()
    legacy_device = iOS(ip, name)

    ip, name = getWatch()
    watch = watchOS(ip, name)

    return legacy_device, watch


if __name__ == "__main__":
    attenuator, upv, sniffer = set_up_equipment()
    phone, watch = set_up_devices()
    bitacorra = Logger()

    this_test = TriangleSingleSweep(
        sniffer = sniffer,
        attenuator= attenuator, 
        bitacorra=bitacorra, 
        device=phone, 
        output=PATHNAME, 
        legacy=True, 
        upv=upv, 
        secondary_device=watch
        )
    
    sweep = np.arange(0, 50, 10)
    offset = 12
    iterations = 3
    
    this_test.test(sweep, iterations, offset)   
