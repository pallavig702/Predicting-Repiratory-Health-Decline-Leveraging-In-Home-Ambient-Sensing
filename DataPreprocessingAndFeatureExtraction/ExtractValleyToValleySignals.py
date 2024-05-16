import math
import statistics
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks
from scipy.signal import find_peaks


##################################################################################################
######################## Extracting the signals starting and ending at valleys ###################
##################################################################################################
def ExtractSignals(data,SigData):
    Start=10000
    End=0
    
    r_pvs = data['resp_pvs'].to_list() # peak or valley (-1 or 1)
    r_vals = data['resp_pv_vals'].to_list() # value of peaks or valleys amplitude
    r_hts = data['resp_pv_hghts'].to_list() # heights of peaks or valleys
    r_time = data['resp_pv_dt_IE'].to_list() # time at peaks and valleys
    r_INDEX = data['INDEX'].to_list()
    
    #print(SigData)
    #for i in range(len(r_pvs)):
    #    print(i,"=>",r_INDEX[0]-r_INDEX[i],r_INDEX[i],r_pvs[i],r_vals[i],SigData[r_INDEX[0]-r_INDEX[i]])
    
    ###############################################################################
    ######################## Getting the FIRST VALLEY VALUE #######################
    ###############################################################################
    for i in range(len(r_pvs)-1):
        #print("From ExtractValleyToValleySignals Script",r_pvs[i])
        if (Start==10000 and r_pvs[i]==-1):
            Start=r_INDEX[0]-r_INDEX[i]
            startValleyVal=r_vals[i]
            sin=r_INDEX[i]
    
    ###############################################################################
    ######################## Getting the LAST VALLEY VALUE #######################
    ###############################################################################  
    for i in reversed(range(len(r_pvs))):
        if (End==0 and r_pvs[i]==-1):
            End=r_INDEX[0]-r_INDEX[i]
            endValleyVal=r_vals[i]
            ein=r_INDEX[i]
    
    ###############################################################################
    ######################## Getting INDEX for FIRST and LAST VALLEY values #######
    ########################### FOR SIGNAL SEGMENTATION ###########################
    ####  Could not use index because of the time stamps were not having exact #### 
    ## millisecond cut offs #######################################################
    ###############################################################################  
    SigIndex=0
    for j in SigData:
        if startValleyVal==j:
            Sig_StartIndex=SigIndex
        elif endValleyVal==j:
            Sig_EndIndex=SigIndex
        SigIndex=SigIndex+1
            
    return(SigData[Sig_StartIndex:Sig_EndIndex])
    
    
