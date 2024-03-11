####################################################################################
#### This package contains the filters applied to composite bed sensor signal ######
####################################################################################

import random
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt


def Interpolation(sub_res2,ColName):
    dfs=sub_res2[['TimeStamp',ColName]]
    #dfs['TimeStamp'] = pd.to_datetime(dfs['TimeStamp'])
    dfs.index = dfs['TimeStamp']
    oidx = dfs.index
    nidx = pd.date_range(oidx.min(), oidx.max(), freq='10ms')
    res=dfs.reindex(oidx.union(nidx)).interpolate('index').reindex(nidx)
    res.drop
    res=res.drop(columns=['TimeStamp'])
    res.reset_index(inplace=True)
    res=res.rename({'index':'TimeStamp'}, axis=1)
    return(res)

####################################################################################
#### Butterworth lowpass filter with a threshold of 0.7Hz of Respiration Signals ###
####################################################################################
def butter_lowpass_filter(data):
    filterorder = 2
    fc_down=0.7
    cutoff=0.014 # fc_down/(fs/2) [fs is frequency of samples which is 100 samples/sec. This comes from previous signal processing steps]

    # Get the filter coefficients
    b, a = butter(filterorder, cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def bandpass(vector):
    [b,a] = butter(3, [0.002,0.014],btype='band');  #0.7-10Hz
    f_filtered = lfilter(b,a,vector)
    return f_filtered
