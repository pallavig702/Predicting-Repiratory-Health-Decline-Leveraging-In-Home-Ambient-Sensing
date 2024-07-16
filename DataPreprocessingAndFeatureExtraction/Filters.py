import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy import signal
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
from scipy.signal import freqz

def bed2df(filename):
    #convert bed3 file to dataframe
    df = pd.read_csv(str(filename), sep='\t', header=5).reset_index()
    df.columns = ['sample', 'date', 'raw1', 'raw2', 'raw3', 'raw4', 'filt1', 'filt2', 'filt3', 'filt4']
    df = df.drop(['sample','date', 'raw1','raw2','raw3','raw4'], axis=1)
    return df

def filterData(vector):
    # 3rd order polynomial, 0.4-10hz bandpass
    fcupper = 10  # Cut-off frequency of the filter
    fclower = 0.7
    fs = 1000
    wu = fcupper / (fs / 2) # Normalize the frequency
    wl = fclower / (fs / 2)
    b, a = butter(3, [wl,wu], btype='band')#signal order, freq limit, type
    filtered = lfilter(b, a, vector)
    return filtered

def butter_bandpass(lowcut, highcut, fs, order):
    # filter design
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    #b, a = butter(order, [low, high], btype='band')
    b, a = butter(order, [lowcut, highcut], btype='band')
    return b, a

def butter_bandpass_filter(data):
    # filter
    order=2
    fs = 100
    lowcut = 0.002 # 0.7
    highcut = 0.014 #10.0
    
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def butter_lowpass_filter(data,filterorder):
    #filterorder = 2   #software filtering 6 order filtering. Refer Zaid's paper while writing own
    fc_down=0.7
    cutoff=0.014 # fc_down/(fs/2) [fs is frequency of samples which is 100 samples/sec. This comes from previous signal processing steps]

    # Get the filter coefficients
    b, a = butter(filterorder, cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def bandpass(vector):
    [b,a] = butter(2, [0.002,0.014],btype='band');  #0.1-0.7hz
    f_filtered = lfilter(b,a,vector)
    return f_filtered


def applyFilter(df):
    filtdf = pd.DataFrame()
    for col in df:
        filtdf[col] = filterData(df[col])
    return filtdf

def splitData(df):
    # get 5 second epoch
    df_dict = {n: df.iloc[n:n+5000, :] for n in range(0, len(df), 5000)}
    return df_dict

def plotSplit(df,col,colTitle):
    fig, axes = plt.subplots(nrows=4, ncols=1,figsize=(14,10)) #sharex=True,sharey=False,
    df[col+"1"].plot(ax=axes[0]);
    axes[0].set_title(colTitle+" 1");
    plt.ylabel("Pressure")
    df[col+"2"].plot(ax=axes[1]);
    axes[1].set_title(colTitle+" 2");
    plt.ylabel("Pressure")
    df[col+"3"].plot(ax=axes[2]);
    axes[2].set_title(colTitle+" 3");
    plt.ylabel("Pressure")
    df[col+"4"].plot(ax=axes[3]);
    axes[3].set_title(colTitle+" 4");
    plt.ylabel("Pressure")
    plt.xlabel("milliseconds")
    fig.tight_layout()
    #
    
    #plt.rcParams["figure.figsize"] = (40,10)
    plt.show()
    plt.savefig('ManuscriptFig1and7.png', bbox_inches='tight')
