########################################################################################
################# Citations: doi #############################
########################################################################################

import math
import numpy as np
import statistics
import pandas as pd
from math import nan
import statsmodels as sm
from patsy import dmatrices
#from statsmodels.sandbox.tsa import movmean



def MAC2(df,T,ColName):
    
    #Data to be used
    resp_dt=df['TimeStamp'].tolist()
    resp_sig = df[ColName].tolist()
    
    T=400
    
    ########################################################################################
    ################# STEP 1: MATLAB equivalent of moving mean #############################
    ########################################################################################
    df['MAC']=df[ColName].rolling((2 * T)+1, center=True,min_periods=1).mean().round(2)
    MAC=df['MAC'].tolist()
    df['MAC'][:T+1] =  round(np.mean(resp_sig[:((2*T) + 1)]),2) #RespSigMeanFirstHalf
    df['MAC'][len(MAC)-(T):] = round(np.mean(resp_sig[len(resp_sig) - (2 * T)-1:]),2)
    
    ########################################################################################
    ################### STEP 2: Getting up and down intercepts #############################
    ########################################################################################
    up_intercepts=[]
    down_intercepts=[]
    
    for i in range(1,len(df['MAC'].tolist())):
        if ((resp_sig[i-1] < MAC[i-1]) and (resp_sig[i] >= MAC[i])):
            up_intercepts.append(i)
        
        elif ((resp_sig[i-1] > MAC[i-1]) and (resp_sig[i] <= MAC[i])):
            down_intercepts.append(i)
   
    if ((len(down_intercepts)<10) or (len(up_intercepts)<10)):
        return()

    
    ########################################################################################
    #####  #STEP 3: Clean the data so that the signal data starts and ends with a peak #####
    ########################################################################################
    # want first pv to be a peak, so remove early down_intercepts #
    while (down_intercepts[0] < up_intercepts[0]):
        down_intercepts = down_intercepts[1:]
    # want last pv to be a peak, so remove late up_intercepts #
    while (up_intercepts[len(up_intercepts)-1] > down_intercepts[len(down_intercepts)-1]):
        up_intercepts = up_intercepts[0:len(up_intercepts)-1]


    ########################################################################################
    ######  #STEP 4: More cleaning. Incase two peaks or valley occurs consecutively,  ######
    ########## consider the second one. Reducing the two consecutive peaks to one ##########
    ########################################################################################
    
    for i in range(1,len(up_intercepts)):
    #index of down_intercept should be one behind index of up_intercept
        j = i - 1
        while((i <= len(up_intercepts)-1) and (up_intercepts[i] < down_intercepts[j])):
            #this means consecutive up_intercepts
            #keep the second one, per Lu
            up_intercepts = up_intercepts[0:i-1]
            Ext_up = up_intercepts[i:]
            up_intercepts.extend(Ext_up)
        
            #now check for consecutive down_intercepts
        j = j + 1    
            # advance index of down_intercept
        while ((j <= len(down_intercepts)-1) and (down_intercepts[j] < up_intercepts[i])):
            #this means consecutive down_intercepts
            #keep the second one, per Lu
            down_intercepts = down_intercepts[0:j-1]
            Ext_down = down_intercepts[j:]
            down_intercepts.extend(Ext_down)
            
    ########################################################################################
    ################### # STEP 5: Cross check if the cleaning is fine ######################
    ########################################################################################           
    if (len(up_intercepts) != len(down_intercepts)):
        print('number of up_intercepts = %d\n',len(up_intercepts))
        print('number of down_intercepts = %d\n',len(down_intercepts))
        print("up intercept is not equal to downcept!")
    else:
        print("Bingo! Code is working well! number of up intercept positions are equal to downcept")
        print('number of up_intercepts = %d\n',len(up_intercepts))
        print('number of down_intercepts = %d\n',len(down_intercepts))
        
        
    ########################################################################################
    ########################### STEP 6: Find Peaks And Valleys #############################
    ########################################################################################
    #pv_index = 0;
    resp_pv_vals=[]
    resp_pv_dt=[]
    resp_pv_idx=[]
    resp_pv_dt_IE=[]
    for i in range(len(up_intercepts)):
        #find peak
        seg_peak_val = max(resp_sig[up_intercepts[i]:down_intercepts[i]]) 
        #seg_peak_index = resp_sig[up_intercepts[i]:down_intercepts[i]].index(seg_peak_val)
        seg_peak_index =resp_sig.index(seg_peak_val,up_intercepts[i],down_intercepts[i])
        
        resp_pv_dt_IE.append(resp_dt[seg_peak_index])
        resp_pv_vals.append(seg_peak_val)
        resp_pv_idx.append(seg_peak_index)
        
        #find subsequent valley (but remember there is not valley after last peak
        if (i < len(up_intercepts)-1):
            seg_valley_val = min(resp_sig[down_intercepts[i]:up_intercepts[i+1]]);
            seg_valley_index = resp_sig.index(seg_valley_val,down_intercepts[i],up_intercepts[i+1])
            
            resp_pv_dt_IE.append(resp_dt[seg_valley_index])
            resp_pv_vals.append(seg_valley_val)
            
    ########################################################################################
    ################################# #STEP 7: PREAMBLE ####################################
    ########################################################################################
    #at this point, we know the first and last element of the sorted vectors are peaks
    #calculate peak heights
    #first is a peak
    
    resp_pv_hghts=[]
    i = 0 
    resp_pv_hghts.append(round(resp_pv_vals[i] - resp_pv_vals[i+1],2))
    #every Even peak [Odd in matlab because of indexing] up to (but not including) the 
    #last is surrounded by two deep valleys

    #NOT ANY MORE --> find the max of the two distance.

    #STEP 7: Now measuring the height of the peakvabove the moving average curve (MAC).
    #every even number is a valley --- set height to 0  
    #print(len(resp_pv_vals),len(MAC),len(resp_pv_idx),len(resp_pv_vals))
    j=1
    for i in range(1,(len(resp_pv_vals)-1)):
        if (i%2 != 0):
        # if i is even, we have a valley
        # set height to 0;
            resp_pv_hghts.append(0)
        else:
            # Changing definition of peak height to be relative to the MAC.
            # otherwise, find max of distance to each valley
            # resp_pv_hghts(i) = max([resp_pv_vals(i) - resp_pv_vals(i-1),...
            # resp_pv_vals(i) - resp_pv_vals(i+1)]);
            resp_pv_hghts.append(round((resp_pv_vals[i] - MAC[resp_pv_idx[j]]),2))
            j=j+1
    
    #last element is a peak
    i = len(resp_pv_vals)-1
    #resp_pv_hghts(i) = resp_pv_vals(i) - resp_pv_vals(i-1);
    resp_pv_hghts.append(round(resp_pv_vals[i] - MAC[resp_pv_idx[j]],2))
    #resp_pv_hghts.append(round(resp_pv_vals[i] - resp_pv_vals[i+1],2))
    # MODIFYING THIS .... NEED MORE WORK HERE
    print(len(resp_pv_hghts)-1)
    
    
    #STEP 8: FINDING QUANTILES To remove the noise in further steps
    x=np.array(resp_pv_hghts[0:len(resp_pv_hghts):2])
    lower_quantile = np.percentile(resp_pv_hghts[0:len(resp_pv_hghts):2], 75, interpolation='midpoint') * 0.5
    upper_quantile = np.percentile(x, 75, interpolation='midpoint') * 2.5
    
    
    ##STEP 8:
    resp_pvs=[]
    ind=0
    for i in range(len(resp_pv_hghts)):
        if (resp_pv_hghts[i] == 0):
            resp_pvs.append(-1)
            ind=ind+1
        elif (resp_pv_hghts[i] > upper_quantile):
            resp_pvs.append(nan)
            # set resp_pv_vals to NaN for noise/motion peak
            resp_pv_vals[i] = nan
            #resp_pv_vals[i-1] = nan
            #resp_pv_vals[i+1] = nan
            # MAY NEED TO REMOVE THIS
            # set heights of noise to NaN
            resp_pv_hghts[i] = nan
            ind=ind+1
        else:
            resp_pvs.append(0)
                
    print(">>",ind, len(resp_pv_hghts))
    
    
    #STEP 9: Labelling the peaks
    for i in range (len(resp_pv_hghts)):
        #lower_quantile = prctile(resp_pv_hghts[1:length(resp_pv_hghts):2], 50)* 0.75
        lower_quantile = np.percentile(resp_pv_hghts[1:len(resp_pv_hghts):2], 50, interpolation='midpoint') * 0.75
        
        if (resp_pv_hghts[i] == 0):# and (i%2!=0):
            #this is a valley
            #print(i,resp_pv_hghts[i])
            resp_pvs[i] = -1
        else:
            if(math.isnan(resp_pv_hghts[i]) or (i < 80)):
                #print(i,len(resp_pvs))
                resp_pvs[i] = np.nan
            else:
                #peaks_to_consider = [(i-80):(i-1):2]
                Get=pd.Series(resp_pv_hghts[(i-80):(i-1):2])
                if Get[::-1].isnull().all():
                    #display(Get.head())
                    continue
                Trailing=6 #Trailing 
                Forward=0 # Forward
                WL = Trailing+Forward+1 #Window Length
                peak_hght_baseline = max(Get[::-1].rolling(WL, min_periods=Forward).median().shift(-Trailing)[::-1].dropna())
                #max(movmedian(resp_pv_hghts[(i-80):(i-1):2], [6 0], 'omitnan', 'Endpoints', 'discard'));
                if (resp_pv_hghts[i] < (peak_hght_baseline * 0.5)):
                    if (resp_pv_hghts[i] < (peak_hght_baseline * 0.1)):
                        #call this apnea
                        resp_pvs[i] = -0.33
                    else:
                        #call this hypopnea
                        resp_pvs[i] = 0.33
                        #set resp_pv_vals to 0 for "apnea peak"
                        #resp_pv_vals(i) = 0;
                else:
                    #these are "good" respiration peaks
                    resp_pvs[i] = 1

    for i in range(0,(len(resp_pvs)-2),2):
        if (resp_pvs[i] < 1):
            if (resp_pvs[i+2] < 1):
                #set any valley between two "apnea peaks" to zero
                resp_pvs[i+1] = 0
    
    from collections import Counter
    counter_object = Counter(resp_pvs)
    print(counter_object)
    print(len(resp_pv_vals),len(resp_pvs),len(resp_pv_dt),len(resp_pv_hghts), len(MAC),\
         len(up_intercepts), len(down_intercepts))
    #print(resp_pvs)
    
    """
    d = {'resp_pvs':resp_pvs,\
        'resp_pv_vals':resp_pv_vals,\
         'resp_pv_hghts':resp_pv_hghts,\
         'resp_pv_dt':resp_pv_dt}
    """
    d = {'resp_pvs':resp_pvs,\
        'resp_pv_vals':resp_pv_vals,\
         'resp_pv_hghts':resp_pv_hghts,\
         'resp_pv_dt_IE':resp_pv_dt_IE}
         

    Res_df = pd.DataFrame(d)
    #display(Res_df.head())
    return(Res_df)
    
