##Purpose: Detecting peaks and valleys with some cacliberations to avoid minor pressure signals noise
##Input: Pandas dataframe Signal Data with time stamps
##OutPut: Pandas datarame with the following columns:
### resp_pvs contains the values -1 (representing valleys), 1 (representing peaks)
##'resp_pv_vals' contains the signal values for each of the valley peak etc.
##'resp_pv_dt_IE' contains time stamps corresponding to each of the peak, valley etc.
###'INDEX': contains the index of the peak and valley in a given time window.

import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks
from scipy.signal import find_peaks

def Find_Peaks(df,ColName):
    resp_dt=df['TimeStamp'].tolist()
    resp_sig = df[ColName].tolist()

    ######################################################################################
    ################################# Initializations ####################################
    ######################################################################################
    #prominences = peak_prominences(resp_sig, index)[0]
    resp_pv_dt_IE=[]
    resp_pv_vals=[]
    resp_pvs=[]
    resp_pv_hghts=[]
    num=0
    INDEX=[]
    skip=[]
    i=0
    
    ######################################################################################
    ############################# Finding Peaks and their index ##########################
    ######################################################################################
    index = find_peaks(resp_sig,height=20)[0]
    
    ######################################################################################
    ########################### Calculating Valleys and their index ######################
    ######################################################################################
    while(i<len(index)-1):
        diff_bet_peaks=resp_sig[index[i]]-resp_sig[index[i+1]]
        if((diff_bet_peaks<0) & ((resp_sig[index[i]]-(min(resp_sig[index[i]:index[i+1]])))<5)):
            i=i+1
            continue
            
        resp_pv_vals.append(resp_sig[index[i]])
        resp_pv_dt_IE.append(resp_dt[index[i]])
        resp_pvs.append(1)
        resp_pv_hghts.append(0)
        INDEX.append(index[i])
        
        #Valleys
        if(i<len(index)-2):
            seg_valley_val=min(resp_sig[index[i]:index[i+1]])
            seg_valley_index = resp_sig.index(seg_valley_val,index[i],index[i+1])
            hts=resp_sig[index[i+1]]-seg_valley_val
            diff=resp_sig[index[i+1]]-(min(resp_sig[index[i]:index[i+1]]))
            if ((i>0)& ((resp_sig[index[i+1]]-(min(resp_sig[index[i]:index[i+1]])))<5)):
                j=i
                
                while(((resp_sig[index[j+1]]-(min(resp_sig[index[j]:index[j+1]])))<5) and (j<len(index)-3)):
                    j=j+1
                    
                if (j<len(index)-2):
                    j=j+1
                   
                seg_valley_val=min(resp_sig[index[j-1]:index[j]])
                seg_valley_index = resp_sig.index(seg_valley_val,index[j-1],index[j])
                
                INDEX.append(seg_valley_index)
                resp_pv_vals.append(seg_valley_val)
                resp_pv_dt_IE.append(resp_dt[seg_valley_index])
                resp_pvs.append(-1)
                resp_pv_hghts.append(0) 
                i=j
                continue
                
            INDEX.append(seg_valley_index)
            resp_pv_vals.append(seg_valley_val)
            resp_pv_dt_IE.append(resp_dt[seg_valley_index])
            resp_pvs.append(-1)
            resp_pv_hghts.append(0)
        i=i+1
        
    ######################################################################################
    ########################### Building and Returning Dataframe #########################
    ######################################################################################
    d = {'resp_pvs':resp_pvs,\
        'resp_pv_vals':resp_pv_vals,\
     'resp_pv_hghts':resp_pv_hghts,\
         'resp_pv_dt_IE':resp_pv_dt_IE,
        'INDEX':INDEX}
            
         
    Res_scipy = pd.DataFrame(d)
    return(Res_scipy)
