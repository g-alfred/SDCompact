"""
This is the only file that will need to be updated when key words change in the bitacorra 
"""
from typing import Tuple, List, Union, Tuple, Dict

def keywords(key : str) -> Dict:
    if key == 'Proxima':
        keymap = {
                'ReTx': ['retrans ratio = ', 'ACL_DATA_STATS[4/10]'],
                'Flush': ['flush counter:', '[ACL_DATA_STATS_EXT][1/4]'],
                'RSSI': ['RSSI = -', 'ACL_DATA_STATS[6/10]',  'high_power_mode'],
                'ReTxPowerIdx': ['retx_power_index='],
                'TxPower': ['tx_power_value=','ACL_DATA_STATS[6/10]',  'high_power_mode'],
                'HDR4': ['HDR4:', '[ACL_DATA_STATS_EXT][3/4]', 'Tx - packet counters:'],
                'HDR8': ['HDR8:', '[ACL_DATA_STATS_EXT][3/4]', 'Tx - packet counters:'],
                'EDR2': ['EDR2:', '[ACL_DATA_STATS_EXT][3/4]', 'Tx - packet counters:'],
                'EDR3': ['EDR3:', '[ACL_DATA_STATS_EXT][3/4]', 'Tx - packet counters:'],
                'CRC': ['bad_crc_ratio:', 'ACL_DATA_STATS[5/10]:'],
                'AFH': [' AFH Channels =','ACL_DATA_STATS[3/10]'],
                'BPS': ['Tx bps =', 'ACL_DATA_STATS[3/10]']
            }
    elif key == 'Primary':
        link_idx = str(0)
        keymap = {
            'ReTx': ['Total Tx retrans ratio:', 'ACL_DATA_STATS['+link_idx+'][5/11]'],
            'Flush': ['flush counter:', '[ACL_DATA_STATS_EXT][1/4]'],
            'RSSI': ['RSSI:', 'ACL_DATA_STATS['+link_idx+'][7/11]','Power level index:'],
            'TxPower': ['power value:     ','RSSI:', 'ACL_DATA_STATS['+link_idx+'][7/11]','Power level index:'],
            'CRC': ['bad_crc_ratio: ', 'ACL_DATA_STATS['+link_idx+'][6/11]'],
            'HDR4': ['HDR4:', '[ACL_DATA_STATS_EXT][3/4]', 'Rx - packet counters:'],
            'HDR8': ['HDR8:', '[ACL_DATA_STATS_EXT][3/4]', 'Rx - packet counters:'],
            'EDR2': ['EDR2:', '[ACL_DATA_STATS_EXT][3/4]', 'Rx - packet counters:'],
            'EDR3': ['EDR3:', '[ACL_DATA_STATS_EXT][3/4]', 'Rx - packet counters:'],
            'AFH': ['Used AFH Channels:', 'ACL_DATA_STATS['+link_idx+'][4/11]'],
            'BPS': ['Rx bps:', 'ACL_DATA_STATS['+link_idx+'][3/11]']
        }
    elif key == 'Secondary':
        link_idx = str(1)
        keymap = {
            'ReTx': ['Total Tx retrans ratio:', 'ACL_DATA_STATS['+link_idx+'][5/11]'],
            'Flush': ['flush counter:', '[ACL_DATA_STATS_EXT][1/4]'],
            'RSSI': ['RSSI:', 'ACL_DATA_STATS['+link_idx+'][7/11]','Power level index:'],
            'TxPower': ['power value:     ','RSSI:', 'ACL_DATA_STATS['+link_idx+'][7/11]','Power level index:'],
            'CRC': ['bad_crc_ratio: ', 'ACL_DATA_STATS['+link_idx+'][6/11]'],
            'HDR4': ['HDR4:', '[ACL_DATA_STATS_EXT][3/4]', 'Rx - packet counters:'],
            'HDR8': ['HDR8:', '[ACL_DATA_STATS_EXT][3/4]', 'Rx - packet counters:'],
            'EDR2': ['EDR2:', '[ACL_DATA_STATS_EXT][3/4]', 'Rx - packet counters:'],
            'EDR3': ['EDR3:', '[ACL_DATA_STATS_EXT][3/4]', 'Rx - packet counters:'],
            'AFH': ['Used AFH Channels:', 'ACL_DATA_STATS['+link_idx+'][4/11]'],
            'BPS': ['Rx bps:', 'ACL_DATA_STATS['+link_idx+'][3/11]']
        }
    return keymap

def device_mapping(device_indx: int) -> Union[str, None]:
    if device_indx == 0:
        return 'Proxima NED'
    elif device_indx == 1:
        return 'Primary'
    elif device_indx == 2:
        return 'Secondary'
    else:
        return None
