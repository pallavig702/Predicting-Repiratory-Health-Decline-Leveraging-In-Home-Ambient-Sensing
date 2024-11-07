
## Called as package from script - Run_FeatureExtractor.py
## This package script performs pre-processing in signal data
# (i) Import data from postgres database
# (ii) Checks if there is too much missing data. if yes then drops the time window
# (iii) Apply butterworth filter to signal
# (iv) Apply Noise detection using MAC algorithm
# (v) Find peaks and valleys in signal
# (vi) Calculate the Restlessness in signal segments

#########################################################################################################
# INPUT: Feeds on -> Raw Signal Data
# OUTPUT: Yields -> Processed Raw Signal Data and feeds processed data into feature extractor package
#########################################################################################################

########################################################
############### Regular Python Packages ################
########################################################
import os
import random
import datetime
import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy import *
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
from matplotlib.backends.backend_pdf import PdfPages
from scipy.signal import butter, filtfilt, find_peaks

########################################################
######## Self Built Functions Import Begins Here# ######
########################################################

############# 1_DATA IMPORT From POSTGRES DB ###########
from GetData import engine
from GetData import query_db
from GetData import get_Raw_data
from functools import partial, reduce

####### 2_FILTERS For Signal Component Extraction ######
from ApplyFilter import butter_lowpass_filter
from ApplyFilter import Interpolation
#from Filters import butter_bandpass_filter

##### 3 Peak Detecteion and Noise Removal Packages #####
from MAC_Function3 import MAC2
from PeakDetection import Find_Peaks

##### 4 Extract Features from Respiration Component #####
from ExtractFeatures import CleanNoise

##### 5 Extract Features from Respiration Component #####
sys.path.append('restlessness/')
from boyusu_restlessness_new_sub_function import boyusu_restlessness_func
from restlessness import determine_restlessness



########################################################################################
######### Get percentage of missing data since we expect 100 data points per sec #######
########################################################################################
def Get_PerCent_Missing_Data(res):
    mini=res.TimeStamp.min()
    maxi=res.TimeStamp.max()
    TimeDiff=(maxi-mini).total_seconds()
    data_len=res.shape[0]
    Expected_len=TimeDiff*100
    Missing_Data_Percentage=((Expected_len-data_len)/Expected_len)*100
    return(Missing_Data_Percentage)


def RunData(Start,End,Res_ID,table,StartEndPath,TIME_WINDOW,ResultFolderPath):
    
    ####################################################################################
    ######################## STEP 1: Import Data of Data 2HOURS ########################
    ####################### Utilizing the timings from Start and End ###################
    ####################################################################################
    result=get_Raw_data(Start,End,Res_ID,engine,table)
    if(result.empty):
        print("Empty Dataframe Found: ",Res_ID,Start,End)
        return()
    
    #####################################################################################
    ###### STEP 2: Check if there is a lot of missing data:Drop 2Hrs Time Window ########
    #####################################################################################
    Missing_Data_Percentage=Get_PerCent_Missing_Data(result)
    if  Missing_Data_Percentage>8:
        print("Lot of missing data in  given time window:",Res_ID,Start,End)
        return()
   
    
    #####################################################################################
    ######################### STEP 3: APPLY BUTTERWORTH LOW PASS FILTER #################
    #####################################################################################
    for index in range(4):
        result['butterf'+str(index+1)]=butter_lowpass_filter(result['filtered'+str(index+1)])
        result['DC_Removed'+str(index+1)]=butter_bandpass_filter(result['butterf'+str(index+1)])
  
    #Retain on butterworth filtered respiration signal data and remove the hardware filtered data
    result=result.drop(columns=['filtered1','filtered2','filtered3','filtered4'])
    

    #####################################################################################
    ################################### STEP4: Apply MAC ################################
    #####################################################################################
    
    Res1=MAC2(result[['butterf1','TimeStamp']],400,'butterf1')
    Res2=MAC2(result[['butterf2','TimeStamp']],400,'butterf2')
    Res3=MAC2(result[['butterf3','TimeStamp']],400,'butterf3')
    Res4=MAC2(result[['butterf4','TimeStamp']],400,'butterf4')
    
    if((len(Res1) == 0) and (len(Res2)==0) and (len(Res3)==0) and (len(Res4)==0)):
        print("Empty Dataframe Found After MAC Detection:",Res_ID,Start,End)
        return()
    
    Res = {'Res1':Res1[['resp_pvs','resp_pv_vals','resp_pv_dt_IE','resp_pv_hghts']], 
    'Res2':Res2[['resp_pvs','resp_pv_vals','resp_pv_dt_IE','resp_pv_hghts']],
      'Res3':Res3[['resp_pvs','resp_pv_vals','resp_pv_dt_IE','resp_pv_hghts']],
      'Res4':Res4[['resp_pvs','resp_pv_vals','resp_pv_dt_IE','resp_pv_hghts']]}
    
    #####################################################################################
    ########################## STEP5: FIND PEAKS PYTHON PACKAGE #########################
    #####################################################################################
    
    print("Started P1")
    P1=Find_Peaks(result[['butterf1','TimeStamp']],'butterf1')
    print("Started P2")
    P2=Find_Peaks(result[['butterf2','TimeStamp']],'butterf2')
    print("Started P3")
    P3=Find_Peaks(result[['butterf3','TimeStamp']],'butterf3')
    print("Started P4")
    P4=Find_Peaks(result[['butterf4','TimeStamp']],'butterf4')
    print("Ended P4")
    if((len(P1) == 0) and (len(P2)==0) and (len(P3)==0) and (len(P4)==0)):
        print("Empty Dataframe Found After Peak Detection: ",Res_ID,Start,End)
        return()
    
    
    Peaks = {'P1':P1[['resp_pvs','resp_pv_vals','resp_pv_dt_IE','resp_pv_hghts','INDEX']], 
    'P2':P2[['resp_pvs','resp_pv_vals','resp_pv_dt_IE','resp_pv_hghts','INDEX']],
      'P3':P3[['resp_pvs','resp_pv_vals','resp_pv_dt_IE','resp_pv_hghts','INDEX']],
      'P4':P4[['resp_pvs','resp_pv_vals','resp_pv_dt_IE','resp_pv_hghts','INDEX']]}
    
    
    #######################################################################################
    ########################## STEP 6: CALL RESTLESSNESS ALGORITHM ########################
    #######################################################################################
    Restlessness = determine_restlessness(result['raw1'].to_list(),result['raw2'].to_list(),result['raw3'].to_list(),\
                                          result['raw4'].to_list(),result['TimeStamp'].to_list())
    
    
    #############################################################################################
    ########### STEP 7: CALL FEATURE EXTRACTION, LABEL NOISY WINDOWS AND PRINT FEATURES  ########
    #############################################################################################
    #WindowWiseData=CleanNoise(result,Res,Peaks,TIME_WINDOW,Res_ID,StartEndPath,ResultFolderPath,Restlessness)
    #return(WindowWiseData)
    CleanNoise(result,Res,Peaks,TIME_WINDOW,Res_ID,StartEndPath,ResultFolderPath,Restlessness)
    return()
