########################################################
############### Regular Python Packages ################
########################################################
import os,sys
import numpy as np
import pandas as pd

import math
import statistics
from scipy import stats

from matplotlib.pyplot import *
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from matplotlib.backends.backend_pdf import PdfPages

########################################################
######## Self Built Functions Import Begins Here# ######
########################################################
from Get_IE_Ratio import Calculate_IE_Ratio
from ExtractValleyToValleySignals import ExtractSignals
#from ExtractValleyToValleySignals2 import ExtractSignals2
from CalculateFeaturesPerWindow import Calculate_B_2_B_Features
from ExtractPeakToPeakFeatures import Calculate_Breath_To_Breath_Features
from HouseKeepingFunctions import CheckFileExistence,GetMinTimeStampWhere_v1Pv2_Start


def CreateDirectory(MYDIR):
    CHECK_FOLDER = os.path.isdir(MYDIR)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(MYDIR)
        print("created folder : ", MYDIR)
    else:
        print(MYDIR, "folder already exists.")
        

def CleanNoise(Sigdata,MACRes,FPeaks,TIME_WINDOW,ResID,StartEndPath,ResultDir,Restless):
    
    #################################################################################
    ######## STEP 1: GETTING SOME INITIALIZATIONS AND PREPROCESSING DONE ############
    ################################################################################# 
    Data=[]
    Features_Cluster=[]
    
    ###################### DATATYPE OF TIMESTAMP SET TO DATETIME ###################
    Sigdata['TimeStamp']=pd.to_datetime(Sigdata['TimeStamp'])
    
    ############## GETTING MIN TIME IN TIMESTAMP (in a given chunk of data)#########
    df1=Calculate_IE_Ratio(MACRes['Res1'])
    x=df1.Start.min()
    
    
    ################################################################################
    ###### STEP 2: CREATING A RESULT DIRECTORY with 2hours start end time window####
    ################################################################################
    
    ################### Creating of directories for output path ####################
    Path=ResultDir
    CreateDirectory(Path+"/"+str(ResID)+"/")
    CreateDirectory(Path+"/"+str(ResID)+"/"+StartEndPath)
    
    ############ FilePath - to Output Feature extracted for Clustering #############
    Features_Cluster_file = Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
            str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+"Features_Cluster.csv"
                                             
    #Plot_TimeWindows(Path)
    ######################### CHECKING RESULTS FILE EXISTENCE ########################
    CheckFileExistence(Features_Cluster_file)                                          
    
    ###################################################################################
    ################## STEP 3: RUN IN A LOOP 2 HOURS TIME WINDOW ######################
    #### Segment Data into 60 sec windows to extract features from minute changes #####
    ###################################################################################
    while x <= df1.End.max():
        
        Raw=dict() ## THIS WAS UNCOMMENTED #CHECK                                      
  
        first=x # start of the time window
        x=pd.to_datetime(x + pd.to_timedelta(TIME_WINDOW, unit='s')) #End of the time window
        
        #####################################################################################
        ########### STEP 3.1: sub_res2 = SEGMENTED TIME_WINDOW OF 60-SEC LENGTH #############
        #####################################################################################
        sub_res2=Sigdata[(Sigdata["TimeStamp"] >= first) & (Sigdata["TimeStamp"]<=x)
        
        #####################################################################################
        ########## STEP 3.2: CHECKPOINT IF LESS THAN (TIME_WINDOW*100) DATA POINTS ##########
        ################### DATA CLEANING STEP FOR MISSING OR POOR DATA #####################                 
        #####################################################################################
        ### DO NOT PROCESS the time windows with lesser number of data points #########
        # As per sample frequency 100 samples/sec there should be 60*Minute*100 samples. 
        # Since we are using 60 sec window the maximum number of samples should be 
        # 6000(60*100). We are just limiting to a lower range observed in the data. We 
        # do not want to have bad data for feature extraction so filtering it out.
                        
        NumFsCutOff = (TIME_WINDOW*100)-100
        if(sub_res2.shape[0]<NumFsCutOff):
            continue
            
        ######################################################################################
        ######## STEP 3.3: max_key=SELECTING THE BEST TRANSDUCER #############################
        ######## BestTransducerSelect="butterb"+str(max_key) ## CHANGED HERE FOR BUTTER B ####
        ######################################################################################    
        Raw[1]=sub_res2['raw1'].sum()
        Raw[2]=sub_res2['raw2'].sum()
        Raw[3]=sub_res2['raw3'].sum()
        Raw[4]=sub_res2['raw4'].sum()
        max_key = max(Raw, key=Raw.get) #GET THE BEST TRANSDUCER NUMBER
        BestTransducerSelect="butterf"+str(max_key) #GET THE BEST TRANSDUCER NAME+NUMBER
        BestTransducerDCRemovedSelect="DC_Removed"+str(max_key)
                         
        ######################################################################################
        ############### STEP 3.4: MAC_BestTransducer,FPeaks_BestTransducer ###################
        ############### SELECTING THE BEST TRANSDUCER SIGNAL SUBSET PEAKS ####################
        ######################################################################################
        MAC_BestTransducer = MACRes['Res'+str(max_key)]
        sub_MAC_BestTransducer=MAC_BestTransducer\
            [(MAC_BestTransducer["resp_pv_dt_IE"] >= first) & (MAC_BestTransducer["resp_pv_dt_IE"]<=x)]
        
        FPeaks_BestTransducer = FPeaks['P'+str(max_key)]
        sub_FPeaks_BestTransducer=FPeaks_BestTransducer\
            [(FPeaks_BestTransducer["resp_pv_dt_IE"] >= first) & (FPeaks_BestTransducer["resp_pv_dt_IE"]<=x)]
         
        ######################################################################################
        ############################# STEP 3.5: null values = noise ##########################
        ################## Labeling THE NOISE WINDOWS - yes or no ############################
        ###################################################################################### 
        if sub_MAC_BestTransducer["resp_pv_vals"].isnull().values.any():
            NAsign="yes"
        else:
            NAsign="no"
                                             
        #######################################################################################
        ########### STEP 3.6: CHECKPOINT: Dropping Dysfunctional/bad data Windows  ############
        ######## Checking if number of peaks > 5, where the usual expectation is 12-18bpm #####
        #######################################################################################
        
        # First CheckPoint
        NumPeaks = sub_FPeaks_BestTransducer[sub_FPeaks_BestTransducer['resp_pvs']==1] 
        if(NumPeaks.shape[0]<5 or len(sub_MAC_BestTransducer['resp_pv_vals'].to_list())<2):
            continue
        
        # Second CheckPoint
        var=statistics.variance(sub_MAC_BestTransducer['resp_pv_vals'].to_list())
        if ((len(sub_MAC_BestTransducer['resp_pvs'].to_list())<=3) & (var<=0.5)):
            continue
            
        ######################################################################################
        ###################### STEP 3.7: CALCULATE RESTLESSNESS BEGINS #######################
        ######################################################################################
        SubRestless=Restless[(Restless['starts_motion'] >= first) & (Restless['ends_motion']<=x)]
        #test=pd.DataFrame()
        SRest=SubRestless.groupby('motion_strength_level')['motion_duration_in_second'].sum()
                                             
        if(pd.DataFrame(SRest).shape[0]>0):
            SubResttest=pd.DataFrame(SRest).rename(columns={'motion_duration_in_second':'Count'}).reset_index()
            
            if (SubResttest.loc[SubResttest['motion_strength_level'] == 3].shape[0]>0):
                Restlessness3Sec=SubResttest.loc[SubResttest['motion_strength_level'] == 3, 'Count'][0]
            else:
                Restlessness3Sec=0

            if (SubResttest.loc[SubResttest['motion_strength_level'] == 2].shape[0]>0):
                Restlessness2Sec=SubResttest.loc[SubResttest['motion_strength_level'] == 2, 'Count'][0] # What if this is empty
            else:
                Restlessness2Sec=0

            if (SubResttest.loc[SubResttest['motion_strength_level'] == 1].shape[0]>0):
                Restlessness1Sec=SubResttest.loc[SubResttest['motion_strength_level'] == 1, 'Count'][0]
            else:
                Restlessness1Sec=0
        else:
            Restlessness3Sec=0
            Restlessness2Sec=0
            Restlessness1Sec=0
           
        ########################################################################################
        ################################ STEP 3.8:CALCULATE FEATURES  ##########################
        ######################################################################################## 
        myFeatures=[]
        myFeatures=[str(first)+"_"+str(x),NAsign,Restlessness3Sec,Restlessness2Sec,Restlessness1Sec]  
        myFeatures.extend(Calculate_B_2_B_Features(sub_FPeaks_BestTransducer,\
        #ImagesPath+str(first)+"_"+str(x)+".png"))

        sub=pd.DataFrame()
        sub=sub_FPeaks_BestTransducer[sub_FPeaks_BestTransducer['resp_pvs']==1]
        RespRate=len(sub['resp_pvs'].to_list())
        myFeatures.extend([RespRate])
        Features_Cluster.append(myFeatures)
        
    ########################################################################################
    ############# WRITING FEATURES EXTRACTED TO PANDAS AND THEN TO A FILE AT ONCE ##########
    ########################################################################################
                                                   
    Features_Cluster_Cols = ["Start_End","NAsign",'Restlessness3Sec','Restlessness2Sec','Restlessness1Sec','Ru_RMSSD','Ru_mDI','Ru_MADI','Ru_RespRate','Ru_SD_RR','Ru_RMDA','Ru_RMI','Ru_A_RMSi', 'Ru_A_RMSe', 'Ru_RMDA_RMS','A_Mean_i', 'A_Mean_e','ht_Mean_av','ht_Mean_max','ht_RMS_av','ht_RMS_max', 'A_inter_mean', 'A_inter_RMS', 'RespRateFromNewPeaks']
    FeaturesCluster=pd.DataFrame(Features_Cluster,columns=Features_Cluster_Cols)
    FeaturesCluster.to_csv(Features_Cluster_file,index=False)

    return()
    #return(dfx)
                   
