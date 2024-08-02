"""
Last Edited : Alfredo Gonzalez 
    Date: 07/31/2024
"""

import os, sys
from .utils.keywords import *
from .attenuator.attenuator import Attenuator
from .sniffer.EllisysSniffer import EllisysSniffer

class btparser():
    def __init__(self, directory : str, sniffer : EllisysSniffer, sniffer_flag=True, legacy_flag=False) -> None:
        self.directory = directory
        self.sniffer = sniffer
        self.sniffer_flag = sniffer_flag
        self.legacy_flag = legacy_flag
    
    def _device_mapping(self, device_indx: int) -> Union[str, None]:
        return device_mapping(device_indx)
        
    def _fetch_keywords(self, keyword: str, device_idx: int = 0) -> Union[Tuple[List[str], str], Tuple[None,None]]:
        """
        When adding new keywords keep in mind that it must be a List in the dictionary
        The numerical values will be extracted from the occurence of the first element
        The other elements in the list is to indicate that those occurences must be present but are not used to find the numerical values
        Make sure the first item doens't have any literals! ex: /[]
        """
        keymap = keywords(self._device_mapping(device_idx))

        if keyword not in keymap:
            # ignore known cases
            # Secondary and Primary don't have retransmission power index
            if (keyword == 'ReTxPowerIdx') and (
                    (self._device_mapping(device_idx) == 'Primary') or (self._device_mapping(device_idx) == 'Secondary')):
                return None, None #this si dirty
            print("You haven't defined the case " + keyword + " for device " + str(device_idx))
            return None, None #this is dirty

        if keyword == 'TxPower':
            pattern = f'({keymap[keyword][0]}.{{2}})'
        elif (keyword == 'BPS') and (self._device_mapping(device_idx) == 'Proxima NED'):
            pattern = f'({keymap[keyword][0]}.{{7}})'
        else:
            pattern = f'({keymap[keyword][0]}.{{5}})'
        return keymap[keyword], pattern

    def _fetch_params_bita(self, bita_df: pd.DataFrame, arg: str) -> pd.Series:
        if arg == 'device':
            return bita_df['dev_id']
        if arg == 'data':
            return bita_df['text']

    def _parse_txbeamformingmetrics(self, df : pd.DataFrame = None) -> pd.DataFrame:
        data = df.to_numpy()
        data = data.flatten().astype('str')

        reTxNbr = []
        ePAPackets = []
        ePABeamformingPackets = []
        syncTimeout = []

        for d in data:
            if 'Total retx packets' in d:
                marker = find_all_occurrences(';', d)
                temp = d[marker[0]-4:marker[0]] #total retx packets
                reTxNbr.append(float(temp))
                temp = d[marker[1]-4:marker[1]] #total ePA packets
                ePAPackets.append(float(temp))
                temp = d[marker[2]-4:marker[2]] #beamforming+ePA packets
                ePABeamformingPackets.append(temp)
                temp = d[marker[3]-4:marker[3]] #sync timeout
                syncTimeout.append(temp)

        kpis = {
            'ReTxNmbr': np.array(reTxNbr),
            'ePAPackets' : np.array(ePAPackets),
            'ePABeamformingPackets': np.array(ePABeamformingPackets),
            'SyncTimeout': np.array(syncTimeout)
        }
        kpis = pd.DataFrame.from_dict(kpis, orient='index').transpose()
        return kpis

    def _parse_linkqualitymetrics(self, df : pd.DataFrame = None ) -> pd.DataFrame:
        data = df.to_numpy()
        data = data.flatten().astype('str')
        rssi = []
        flush = []
        txpower =  []
        for d in data:
            if 'RSSI' in d:
                temp = float(d[-4:])
                rssi.append(temp)
            if 'TxPwr' in d:
                temp = ''.join(self._remove_non_numeric(d, False))
                temp = float(temp)
                txpower.append(temp)
            if 'TxFlush' in d:
                temp = ''.join(self._remove_non_numeric(d, False))
                temp = float(temp)
                flush.append(temp) 

        longest = max(len(txpower), len(flush), len(rssi))
        device_name = np.repeat('Legacy', longest)
        kpis = {
            'Name': device_name,
            'Flush': np.array(flush),
            'RSSI': np.array(rssi),
            'TxPower': np.array(txpower)
        }
        kpis = pd.DataFrame.from_dict(kpis, orient='index').transpose()
        return kpis

    def _parse_bita(self, file: str, device: int = 0) -> pd.DataFrame:
        """
        new kpis have to be added  in fetch_kpi and in this function. reflect it in prepare for plot comments
        """
        bita_df = pd.read_csv(file, low_memory=False)
        devID = self._fetch_params_bita(bita_df=bita_df, arg='device').to_numpy()
        devID = np.unique(devID)[device]
        bita_df = bita_df[self._fetch_params_bita(bita_df, 'device') == devID]
        bita_text = self._fetch_params_bita(bita_df, 'data')

        def fetchKPI(self, df: pd.Series, keyword_for_fetch: str, device_idx: int = 0, save_series=False) -> np.ndarray:
            """
            input:
            df = series containing the text form bitacorra logs
            keyword = ReTx for reported retransmissions
            output:
            np.ndarray of requested kpi
            """
            keyword, pattern = self._fetch_keywords(keyword_for_fetch, device_idx=device_idx)
            if keyword is None:
                return np.array([])

            filter_series = df
            for keys in keyword:
                filter_series = filter_series[filter_series.str.contains(re.escape(keys), case=False, na=False)]
                if filter_series.empty:
                    print("Your keywords are wrong! --> "+keys+" <-- came out empty for device="+self._device_mapping(device_idx))
                    print("Could be something went wrong with the set-up here too...")
                    breakpoint()

            # Filter rows where all keywords are present
            kpi_series = filter_series.str.extract(pattern, flags=re.IGNORECASE, expand=False)
            numeric_series = kpi_series.str.replace(r'\D', '', regex=True)

            if save_series:
                file_path = '/Users/perflab-sd/work/repo/dev/ConnectivityPerformanceAutomation/Logs/test_box/filtered_csvz/'
                save_or_merge_file(file_path, filter_series, keyword_for_fetch + '_' + self._device_mapping(device_idx) )
                file_path = '/Users/perflab-sd/work/repo/dev/ConnectivityPerformanceAutomation/Logs/test_box/kpi_filter/'
                save_or_merge_file(file_path, kpi_series, keyword_for_fetch + '_' + self._device_mapping(device_idx) )
                file_path = '/Users/perflab-sd/work/repo/dev/ConnectivityPerformanceAutomation/Logs/test_box/numeric_filter/'
                save_or_merge_file(file_path, numeric_series, keyword_for_fetch + '_' + self._device_mapping(device_idx) )
                
            return numeric_series.to_numpy().astype(float)

        retrans_rate = fetchKPI(bita_text, 'ReTx', device_idx=device)

        flush_count = fetchKPI(bita_text, 'Flush', device_idx=device)

        rssi = fetchKPI(bita_text, 'RSSI', device_idx=device) * -1

        retx_power = fetchKPI(bita_text, 'ReTxPowerIdx', device_idx=device)

        tx_power = fetchKPI(bita_text, 'TxPower', device_idx=device)

        longest = max(len(retrans_rate), len(flush_count), len(rssi), len(retx_power), len(tx_power))

        device_name = np.repeat(self._device_mapping(device_indx=device), longest)
        kpis = {
            'Name': device_name,
            'ReTx': retrans_rate,
            'Flush': flush_count,
            'RSSI': rssi,
            'ReTxPowerIdx': retx_power,
            'TxPower': tx_power
        }

        kpis = pd.DataFrame.from_dict(kpis, orient='index').transpose()
        return kpis

    def _parse_sniffer(self, sniffer_csv : str = None ) -> None:
        df = pd.read_csv(sniffer_csv)
        packet_types = df['Logical Packet Type'].to_numpy().astype(str)
        unique_packet_types = np.unique(packet_types).tolist()
        if 'nan' in unique_packet_types:
            # unique_packet_types = unique_packet_types.tolist()
            unique_packet_types.remove('nan')
            unique_packet_types = np.array(unique_packet_types)
        original_unique = unique_packet_types.copy()
        for i, pkt in enumerate(unique_packet_types):
            if '-' in pkt:
                unique_packet_types[i] = pkt.replace('-','')
        kpi = {key: [] for key in unique_packet_types}
        for idx, key in enumerate(kpi):
            temp = df['RSSI'][df['Logical Packet Type'] == original_unique[idx]].to_list()
            temp = [float(i.replace('dBm', '')) for i in temp]
            kpi[key] = np.array(temp)
        for key in kpi:
            length = max(length, len(kpi[key]))
        kpi['Name'] = np.repeat('Sniffer', length)
        kpi = pd.DataFrame.from_dict(kpi, orient='index').transpose()
        return kpi
        
    def parse_all(self, parent_directory: str, sniffer: EllisysSniffer = None, sniffer_flag: bool = True,
              bitacora_flag: bool = True) -> None:
        if sniffer is None: sniffer_flag = False

        attenuation_folders = list_folders(parent_directory)
        sorting_idx = np.argsort(remove_non_numeric(attenuation_folders))
        attenuation_folders = np.array(attenuation_folders)[sorting_idx].tolist()  # grr annoying

        # cycling into folders and finding files - format dependent
        if '.DS_Store' in attenuation_folders: attenuation_folders.remove('.DS_Store')
        for attenuation in attenuation_folders:
            print("")
            print('Parsing files in ' + attenuation)
            iterations = os.listdir(parent_directory + '/' + attenuation)
            if '.DS_Store' in iterations: iterations.remove('.DS_Store')
            print("       Parsing Iterations")
            print("              ", end="")
            iterations = np.sort(iterations)
            for iterate in iterations:
                print(iterate.replace('iteration_', ' '), end="")
                current_path = parent_directory + '/' + attenuation
                files = os.listdir(current_path + '/' + iterate)
                if '.DS_Store' in files: files.remove('.DS_Store')
                # actual parsing starts here
                for current_file in files:
                    current_path = parent_directory + '/' + attenuation + '/' + iterate
                    if (current_file == 'snifferFileLocation.csv') and sniffer_flag:
                        temp = pd.read_csv(current_path + '/' + current_file)
                        traceFilePath = temp['TraceFilePath'].to_numpy()[0]
                        sniffer.closeTraceFile()
                        sniffer.loadTraceFile(traceFilePath)
                        snifferFileName = sniffer.convertToCsv(current_path)
                        if 'export_BT_report.csv' in snifferFileName:
                            kpis_sniff =  self._parse_sniffer(current_path+'/export_BT_report.csv')
                            this_attenuation = remove_non_numeric([attenuation])
                            length = len(kpis_sniff['Name'])
                            kpis_sniff['Attenuation'] = np.repeat(this_attenuation[0], length)
                            kpis_sniff.to_csv(current_path+'/parsed_sniff_logs.csv', index=False)
                        else:
                            sys.exit('export_BT_report was not generated')
                        
                    if (current_file.split('.')[-1] == 'csvz') and bitacora_flag:
                        bitaFileName = convert_bita(current_path + '/' + current_file)
                        temp = pd.read_csv(bitaFileName, low_memory=False)
                        dev_id = self._fetch_params_bita(temp, 'device').to_numpy()
                        dev_id = np.unique(dev_id)
                        for this_device in range(len(dev_id)):
                            current_path = parent_directory + '/' + attenuation + '/' + iterate + '/device_' + str(
                                this_device)
                            
                            if self._device_mapping(this_device) is None:                           
                                continue
                            if LEGACY_FLAG and ('Proxima' in device_mapping(this_device)) :
                                lqm_file = parent_directory + '/' + attenuation + '/' + iterate+'/Source_Host_LinkQualityMetrics.txt'
                                lqm_df = pd.read_csv(lqm_file)
                                kpis = parse_linkqualitymetrics(lqm_df)
                                txb_file = parent_directory + '/' + attenuation + '/' + iterate+'/Source_Tx_Beamforming_Report.txt'
                                txb_df = pd.read_csv(txb_file)
                                kpis2 = parse_txbeamformingmetrics(txb_df)
                                kpis = kpis.join(kpis2, how='outer')
                            else:
                                kpis = parse_bita(bitaFileName, this_device)
                            os.makedirs(current_path, exist_ok=True)
                            length = len(kpis['Name'])
                            this_attenuation = remove_non_numeric([attenuation])
                            kpis['Attenuation'] = np.repeat(this_attenuation[0], length)
                            kpis.to_csv(current_path + '/Bitacora.csv', index=False)

    def consolidate(parent_directory : str) -> None:
        attenuation_folders = list_folders(parent_directory)
        dataframe_hold = pd.DataFrame()

        # cycling into folders and finding files - format dependent
        if '.DS_Store' in attenuation_folders: attenuation_folders.remove('.DS_Store')
        attenuation_folders = np.sort(attenuation_folders)
        for attenuation in attenuation_folders:
            print('Organizing files in ' + attenuation)
            iterations = os.listdir(parent_directory + '/' + attenuation)
            if '.DS_Store' in iterations: iterations.remove('.DS_Store')
            iterations = np.sort(iterations)
            for iterate in iterations:
                current_path = parent_directory + '/' + attenuation
                files = os.listdir(current_path + '/' + iterate)
                sniff_df = pd.read_csv(current_path+ '/' + iterate + '/parsed_sniff_logs.csv')
                dataframe_hold = pd.concat([dataframe_hold, sniff_df], ignore_index=True)
                if '.DS_Store' in files: files.remove('.DS_Store')
                # actual parsing starts here
                for current_file in files:
                    current_path = parent_directory + '/' + attenuation + '/' + iterate
                    if 'device_' in current_file:
                        try:
                            bita_df = pd.read_csv(current_path + '/' + current_file + '/Bitacora.csv')
                            dataframe_hold = pd.concat([dataframe_hold, bita_df], ignore_index=True)
                        except:
                            continue

        dataframe_hold.to_csv(parent_directory+'/consolidated.csv', index=False)



