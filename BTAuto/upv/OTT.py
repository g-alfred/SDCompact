'''Connectivity Perf Automation Framework
    Author: Taplabs
    Modified By - Rahil
    Team: Connectivity Performance and Analytics
    Rev: 1.0.0
    Date: October 2018
    Copyright (c) 2018 Apple. All rights reserved

    Change Log

'''
polqa_buff_strings =[
    "POLQA with play",
    "60000",
    "D:\\UPV\\OfflineTestTool\\PlayAndRecord_ScalePFS.set",
    "D:\\UPV\\OfflineTestTool\\OfflinePOLQA_NoAutoGain.set",
    "D:\\UPV\\OfflineTestTool\\Malden_ref.wav",
    #"D:\\UPV\\OfflineTestTool\\Malden_ref_EQprocessed.wav",
    "-8",
    "empty",
    "empty",
    "2",
    "3",
    "empty",
    "empty",
    "empty",
    "1",
    # VolTE, Volume 0.88
    # "0.180", #0.180 for W2 # 0.180
    # "0.180", #0.180 for W2 # 0.180
    # "0.180",  # 0.180 for W2 # 0.180
    # "0.180",  # 0.180 for W2 # 0.180
    # VolTE, Volume 0.3
    # "0.180", #0.180 for W2 # 0.180
    # "0.180", #0.180 for W2 # 0.180
    "0.180",  # 0.180 for W2 # 0.180 (0.300)
    "0.180",  # 0.180 for W2 # 0.180 (0.300)
    "empty",
    "False",
    "empty",
    "empty",
    "empty",
    "True",
    "True",
    "D:\\UPV\\OfflineTestTool\\Degraded",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "True",
    "empty",
    "on",
    "0",
    "empty",
    "0",

]

'''
peaq_buff_strings =[
    "triggered PEAQ",
    "200000",
    "D:\\UPV\\OfflineTestTool\\TriggeredRecord.set",
    "D:\\UPV\\OfflineTestTool\\OfflinePEAQ_Advanced.set",
    #"D:\\UPV\\OfflineTestTool\\PEAQ_Ref_OTT.wav",
    "D:\\UPV\\OfflineTestTool\\PEAQ_Ref_OTT_EQfilt.wav",
    #"D:\\UPV\\OfflineTestTool\\PEAQ_Reference_Filt.wav",
    #"D:\\UPV\\OfflineTestTool\\ContinuousSweep.wav",
    "empty",
    "empty",
    "empty",
    "empty",
    "2",
    "empty",
    "empty",
    "empty",
    "0.318",
    "0.3",
    "0.3",
    "empty",
    "True",
    "0.03",
    "400",
    "True",
    "True",
    "True",
    "D:\\UPV\\OfflineTestTool\\Degraded\\",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "empty",
    "True",
    "empty",
    "on",
    "-15",
    "empty",
    "0"
]
'''

# peaq_buff_strings =[
#     "triggered PEAQ",
#     "180000",
#     "D:\\UPV\\OfflineTestTool\\TriggeredRecord.set",
#     "D:\\UPV\\OfflineTestTool\\OfflinePEAQ_Advanced.set",
#     "D:\\UPV\\OfflineTestTool\\PEAQ_Ref_OTT.wav",
#     #"D:\\UPV\\OfflineTestTool\\PEAQ_Reference_Filt.wav",
#     #"D:\\UPV\\OfflineTestTool\\ContinuousSweep.wav",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "2",
#     "empty",
#     "empty",
#     "empty",
#     "0.318", #0.318 for b188. #0.518 for w2
#     # "0.5",
#     # "0.5",
#     "0.5",#0.3 for w2
#     "0.5",#0.3 for w2
#     "empty",
#     "False",
#     "0.05",
#     "400",
#     "True",
#     "True",
#     "True",
#     "D:\\UPV\\OfflineTestTool\\Degraded\\",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "empty",
#     "True",
#     "empty",
#     "on",
#     "-10",
#     "empty",
#     "0"
# ]

peaq_buff_strings =[
    "triggered PEAQ",  # Command
    "1000000",  # Timeout
    "D:\\UPV\\OfflineTestTool\\TriggeredRecord.set",  # Setup File 1
    "D:\\UPV\\OfflineTestTool\\OfflinePEAQ_Advanced.set",  # Setup File 2
    "D:\\UPV\\OfflineTestTool\\PEAQ_Ref_OTT_EQfilt.wav",  # Signal File
    "empty",  # Gen. Level (dBr)
    "empty",  # Precondition Signal File (Path Name)
    "empty",  # Precondition Gen. Level
    "empty",  # Generator Channel
    "2",  # Analyzer Channels
    "empty",  # Generator filter file (path name)
    "empty",  # Analyzer filter file (path name)
    "empty",  # Decoder Cal Value (V)
    "0.518",  # 0.318 for b188. #0.518 for w2  # Encoder Cal Value (V)
    "0.2",  # 0.3 for w2  # Mobile Output 1 Cal Value (V)
    "0.2",  # 0.3 for w2  # Mobile Output 2 Cal Value (V)
    "empty",  # Mobile Input Cal Value (V)
    "False",  # Ground
    ##"True",  # Ground
    "0.03",  #0.05 default  # Trigger Level (V)
    "400",  # Pretrigger (ms)
    "True",  # Calculate Channel Delay Difference Calculate PEAQ Both Channels
    "True",  # Calculate Delay Channel 1, Calculate PEAQ/POLQA Left Channel
    # "False",  # Calculate Delay Channel 1, Calculate PEAQ/POLQA Left Channel
    "True",  # Calculate Delay Channel 2, Calculate PEAQ/POLQA Right Channel
    # "False",  # Calculate Delay Channel 2, Calculate PEAQ/POLQA Right Channel
    "D:\\UPV\\OfflineTestTool\\Degraded\\",  # Directory for result files
    "empty",  # Sample Rate Ratio
    "empty",  # Correlation Length 1
    "empty",  # Correlation Length 2
    "empty",  # Analysis Length 1
    "empty",  # Analysis Length 2
    "empty",  # Calculation Length 1
    "empty",  # Calculation Length 2
    "empty",  # Speed Factor 1
    "empty",  # Speed Factor 2
    "empty",  # Minimum S/N Ratio 1
    "empty",  # Minimum S/N Ratio 2
    "empty",  # Max. Number of Retrials
    "True",  # Keep Input Parameters
    "empty",  # Strictly Require Parameters
    "on",  # Monitor State
    "0",  # Monitor Volume
    "empty",  # Monitor Signal
    "0"  # Measurement Delay (s)
]

delay_play_strings = [
    "delay",
    "60000",
    "D:\\UPV\\OfflineTestTool\\DelayWaveform.set",
    "empty",
    "D:\\UPV\\OfflineTestTool\\CSS_32k_48kHz.wav",
    "-8",
    "empty",
    "empty",
    "2",
    "3",
    "empty",
    "empty",
    "empty",
    "1",
    "0.1",
    "0.1",
    "empty",
    "False",
    "0.05",
    "empty",
    "True",
    "False",
    "True",
    "D:\\UPV\\OfflineTestTool\\Degraded",
    "16",
    "28800",
    "28800",
    "725",
    "250",
    "4096",
    "8192",
    "1",
    "2",
    "2",
    "2",
    "0",
    "True",
    "empty",
    "on",
    "-10",
    "empty",
    "0"
]

delay_trigger_strings = [
    "triggered delay difference",
    "60000",
    "D:\\UPV\\OfflineTestTool\\DelayWaveform.set",
    "empty",
    "D:\\UPV\\OfflineTestTool\\CSS_32k_48kHz.wav",
    "empty",
    "empty",
    "empty",
    "empty",
    "2",
    "empty",
    "empty",
    "empty",
    "0.318",
    "0.3",
    "0.3",
    "empty",
    "False",
    "0.05",
    "empty",
    "True",
    "False",
    "False",
    "D:\\UPV\\OfflineTestTool\\Degraded",
    "16",
    "28800",
    "28800",
    "725",
    "250",
    "4096",
    "8192",
    "1",
    "1",
    "2",
    "2",
    "0",
    "True",
    "empty",
    "on",
    "-10",
    "empty",
    "0",
    "0",
]



