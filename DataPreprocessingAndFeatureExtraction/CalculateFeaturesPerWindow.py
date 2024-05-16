import math
import statistics
import numpy as np
import pandas as pd

def variance(RespiratoryRate):
    mean=RespiratoryRate
    x=16
   
    deviations = (x - mean) ** 2
    variance = deviations / 1
    return variance
 
def stdev(RespiratoryRate):
    import math
    var = variance(RespiratoryRate)
    std_dev = math.sqrt(var)
    return std_dev


#Consider 2 peaks at a time for the caclulations
def Calculate_B_2_B_Features(data,windowpath):
    #print("window from CalculateFeaturesPerWindow script",windowpath)
    data['resp_pv_dt_IE'] = pd.to_datetime(data['resp_pv_dt_IE'])
    i=0
    Resp_Cycle=1

    r_pvs = data['resp_pvs'].to_list() # peak or valley (-1 or 1)
    r_vals = data['resp_pv_vals'].to_list() # value of peaks or valleys amplitude
    r_hts = data['resp_pv_hghts'].to_list() # heights of peaks or valleys
    r_time = data['resp_pv_dt_IE'].to_list() # time at peaks and valleys
    
    Diff_IE=[]
    count=[]
    Start=[]
    End=[]
    Breath_to_Breath=[] 
    SD_B2B_Inter=[] #successive differences of breath-to-breath intervals
    Sucessive_BtoB_diffenceInAmplitudes=[] # Difference between amplitudes of two sucessive peaks 2nd-1st.
    #Note: Difference between amplitudes of two sucessive valleys is calculated from 
    Sucessive_BtoB_diffenceInHeights=[]
    I_inter=[]
    E_inter=[]
    
    Ai_inter=[]
    Ae_inter=[]
    ht_max=[]
    ht_mean=[]
    A_inter=[]
    while(i<data.shape[0]-9):
        ##################################################################
        ################# CASE 1: Starting with a valley #################
        ##################################################################
        if((r_pvs[i]==-1) and r_pvs[i+1]==1 and r_pvs[i+2]==-1 and r_pvs[i+3]==1):     
            
            #the inspiration and expiration intervals
            I_inter.append((r_time[i+1]-r_time[i]).total_seconds())
            I_inter.append((r_time[i+3]-r_time[i+2]).total_seconds())
            
            E_inter.append((r_time[i+2]-r_time[i+1]).total_seconds())
            if(r_pvs[i+4]==-1):
                E_inter.append((r_time[i+4]-r_time[i+3]).total_seconds())
            else:
                E_inter.append(math.nan)
                
            # The differences of the amplitudes of peaks and valleys for inspiration and expiration are defined as:
            Ai_inter.append(r_vals[i+1]-r_vals[i]) #peaksAmplitudes(P1) - valleyAmplitudes(V1)
            A_inter.append(r_vals[i+1]-r_vals[i])
            
            Ae_inter.append(r_vals[i+1]-r_vals[i+2])#peaks Amplitudes(P1) - valleyAmplitudes(V2)
            A_inter.append(r_vals[i+1]-r_vals[i+2])
            
            Ai_inter.append(r_vals[i+3]-r_vals[i+2])
            A_inter.append(r_vals[i+3]-r_vals[i+2])
            
            maxi_Amp=max(r_vals[i],r_vals[i+2])
            mean_Amp=np.mean([r_vals[i],r_vals[i+2]])
            
            ht_max.append(r_vals[i+1]-maxi_Amp)
            ht_mean.append(r_vals[i+1]-mean_Amp)
            
            if(r_pvs[i+4]==-1):
                Ae_inter.append(r_vals[i+3]-r_vals[i+4])
                A_inter.append(r_vals[i+3]-r_vals[i+4])
                
                maxi_Amp=max(r_vals[i+2],r_vals[i+4])
                mean_Amp=np.mean([r_vals[i+2],r_vals[i+4]])
            
                ht_max.append(r_vals[i+3]-maxi_Amp)
                ht_mean.append(r_vals[i+3]-mean_Amp)
                
            else:
                Ae_inter.append(math.nan)
                A_inter.append(math.nan)
                
                ht_max.append(r_vals[i+3]-r_vals[i+2])
                ht_mean.append(r_vals[i+3]-r_vals[i+2])
      
            # Starts Breath to breath intervals
            B2B_Inter_1=(r_time[i+3]-r_time[i+1]).total_seconds() #Breath to breath intervals (Peak to peak)
            
            if((r_pvs[i+4]==-1) and r_pvs[i+5]==1 and r_pvs[i+6]==-1 and r_pvs[i+7]==1):
                B2B_Inter_2=(r_time[i+7]-r_time[i+5]).total_seconds()
                Diff=abs(B2B_Inter_2-B2B_Inter_1)
                SD_B2B_Inter.append(Diff) #successive differences of breath-to-breath(peak to peak) intervals
            else:
                SD_B2B_Inter.append(math.nan)
            
            # Ends Breath to breath intervals   
            Breath_to_Breath.append((r_time[i+3]-r_time[i+1]).total_seconds())
            Sucessive_BtoB_diffenceInAmplitudes.append(r_vals[i+3]-r_vals[i+1])
            Sucessive_BtoB_diffenceInHeights.append(r_hts[i+3]-r_hts[i+1])
            Start.append(r_time[i])
            if(r_pvs[i+4]==-1): #If ends with a valley -1,1-1,1,-1 = 2 complete Respiration Cycles
                End.append(r_time[i+3])
                #print(len(r_time),i,i+3)
                i=i+4 #Start next cycle at the valley after 2nd respiration peak
            else:
                End.append(r_time[i+3])
                #print(len(r_time),i,i+3)
                i=i+3 #Else, Start next cycle at the peak after 2nd respiration peak
            #print(">>",Breath_to_Breath)
        ###################################################################################################
        ################# CASE 2: None of the above sequence was found for 2 respiration #################
        ##################################################################################################
        else:
            i=i+1
        
        """
        ##CASE 2: Starting with a valley
        elif (r_pvs[i]==1 and r_pvs[i+1]==-1 and r_pvs[i+2]==1): 
            Breath_to_Breath.append((r_time[i+2]-r_time[i]).total_seconds())
            Sucessive_BtoB_diffenceInAmplitudes.append(r_vals[i+2]-r_vals[i])
            Sucessive_BtoB_diffenceInHeights.append(r_hts[i+2]-r_hts[i])
            Start.append(r_time[i])
            if(r_pvs[i+3]==-1): #If ends with a valley -1,1-1,1,-1 = 2 complete Respiration Cycles
                End.append(r_time[i+3])
                i=i+3 #Start next cycle at the valley after 2nd respiration peak
            else:
                End.append(r_time[i+2])
                i=i+2 #Else, Start next cycle at the peak after 2nd respiration
            print("CASE2",(r_time[i+2]-r_time[i]).total_seconds(), r_vals[i+2]-r_vals[i], r_hts[i+2]-r_hts[i])
        """
        
    #d = {'Start':Start,'End':End,'I_E':I_E}
    newSD_B2B_Inter = [x for x in SD_B2B_Inter if math.isnan(x) == False]
    newAi_inter = [x for x in Ai_inter if math.isnan(x) == False]
    newAe_inter = [x for x in Ae_inter if math.isnan(x) == False]
    newA_inter = [x for x in A_inter if math.isnan(x) == False]
    
    newI_inter = [x for x in I_inter if math.isnan(x) == False]
    newE_inter = [x for x in E_inter if math.isnan(x) == False]
    ##########################################################################################################################
    # FEATURE 1: RMSSD - The square root of the mean of the squares of the successive difference of breath-to-breath intervals
    ##########################################################################################################################
    RMSSD=np.sqrt(np.mean(np.square(newSD_B2B_Inter)))

    
    ##########################################################################################################################
    ################### FEATURE 2 - mDI - Mean of successive differences of breath-to-breath intervals #######################
    ##########################################################################################################################
    mDI=np.mean(newSD_B2B_Inter)

    
    ##########################################################################################################################
    #################### FEATURE 3 -  MADI - Maximum absolute differences of breath-to-breath intervals ######################
    ##########################################################################################################################
    if len(newSD_B2B_Inter)==0:
        MADI=math.nan
    else:
        MADI=max(newSD_B2B_Inter)

    ##########################################################################################################################
    ######################### FEATURE 4 - Respiratory Rate #My: Standard deviation from Normal RR15 ##########################
    ##########################################################################################################################
    SD_RR=stdev(r_pvs.count(1))

    ##########################################################################################################################
    ##### FEATURE 5 - RMDA - The ratio of the mean of differences between the amplitudes of expiration and inspiration #######
    ##########################################################################################################################
    A_Mi=np.mean(newAi_inter)
    A_Me=np.mean(newAe_inter)
    RMDA = A_Mi/A_Me
    if(RMDA <0):
        print("issue",RMDA, "\n",windowpath,"\n",A_Mi,A_Me,Ai_inter,Ae_inter)
    
    ##Amplitude Feature
    A_RMSi=np.sqrt(np.mean(np.square(newAi_inter)))
    A_RMSe=np.sqrt(np.mean(np.square(newAe_inter)))
    RMDA_RMS = A_RMSi/A_RMSe
    
    
    #Features 6 - RMI - The ratio of the mean of expiration and inspiration intervals
    I_Mi=np.mean(newI_inter)
    I_Me=np.mean(newE_inter)
    RMI = I_Mi/I_Me 
    
    #Feature 7 - Amplitude Shallowless measurement
    A_Mean_i=np.mean(newAi_inter)
    A_Mean_e=np.mean(newAe_inter)
    
    ht_Mean_av=np.mean(ht_mean)
    ht_Mean_max=np.mean(ht_max)
    
    ht_RMS_av=np.sqrt(np.mean(np.square(ht_mean)))
    ht_RMS_max=np.sqrt(np.mean(np.square(ht_max)))
    
    A_inter_mean=np.mean(newA_inter)
    
    A_inter_RMS=np.sqrt(np.mean(np.square(newA_inter)))
    
    #print("haha",[RMSSD,mDI,MADI,r_pvs.count(1),SD_RR,RMDA,RMI])
    return([RMSSD,mDI,MADI,r_pvs.count(1),SD_RR,RMDA,RMI,A_RMSi,A_RMSe,RMDA_RMS,A_Mean_i,A_Mean_e,ht_Mean_av,ht_Mean_max,ht_RMS_av,ht_RMS_max,A_inter_mean,A_inter_RMS])
    #print(df.dtypes)
    #df.head()
    #print("start")
    #print(data['resp_pv_vals'].to_list())
    #print([RMSSD,mDI,MADI,r_pvs.count(1),SD_RR,RMDA,RMI])
    #print("end")
    
