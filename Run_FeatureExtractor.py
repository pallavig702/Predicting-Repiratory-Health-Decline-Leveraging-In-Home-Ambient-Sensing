# 
#########################################################################################################
# This script is part of STEP 1: Data Preprocessing (cleaning and feature engineering) of signal data from Hydraulic Bed Sensor Data (as mentioned in Readme).
##This script includes the following steps:
# (i) Data import From POSTGRES DB and perform data prepocessing like 
# (ii)extraction of specific frequency signals using butter worth signal frequency filter, 
# (iii)peak and valley detection,
# (iv)noisy peak detection,
# (v)split the data into shorter 60-sec windows and extract feature from each 60-sec window and store them datewise.

#For each day script processes data for 2 hours window chunks in loop until 24 hours  to avoid blocking the memory and avoid out of memory issues.
#########################################################################################################

#########################################################################################################
# INPUT: Feeds on original signal data from postgres DB.
# CALLS PACKAGE FROM FOLDER: DataPreprocessingAndFeatureExtraction/DataRetrievalCycle.py
# OUTPUT: Extracts features for given resident ID, for specific dates and stores them datewise for each resident ID. 
#########################################################################################################



########################################################
############### Regular Python Packages ################
########################################################
import time
import random
import os,sys
import datetime
import numpy as np
import pandas as pd
from sqlalchemy import *
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

########################################################
######## Self Built Functions Import Begins Here# ######
########################################################
sys.path.append("DataPreprocessingAndFeatureExtraction/")

#1_DATA IMPORT
from GetData import query_db
from GetData import get_Raw_data
from GetData import engine

#2_FILTERS
from ApplyFilter import butter_lowpass_filter
from ApplyFilter import Interpolation

#3_SELF_WRITTEN_SCRIPTS
from MAC_Function3 import MAC2
from DataRetrievalCycle import RunData
from HouseKeepingFunctions import CreateDirectory,CheckFileExistence

#############################################################################################
########################Provide here the IDs of the Residents ###############################
#############################################################################################
Res_ids=[3083,3127]
Res=dict()

#############################################################################################
############Provide here Dates For Feature Extraction For Each Resident ID ##################
#############################################################################################
EHRpath='DataPreprocessingAndFeatureExtraction/ProvideDatesForData/'

#############################################################################################
###########SCRIPT RUN STATUS FILE: Check if the status file exists, if yes then delete#######
#############################################################################################
Filename="StatusFile"
CheckFileExistence(Filename)
file1 = open(Filename, "a")

############################################################################################
######### GET IDS FROM THE PATH AND THE DATES FOR WHICH WE PLAN TO RUN THE PIPELINE#########
############################################################################################
for ids in Res_ids:
    print(ids, pd.read_csv(EHRpath+str(ids),index_col=None,header=None)[0].to_list())
    Res[ids]=pd.read_csv(EHRpath+str(ids),index_col=None,header=None)[0].to_list()

#####################################################################################################
################ LOOPING THROUGH EACH ID and ITS DATA and PROCESS IN BLOCKS OF 2 HRS ################
#####################################################################################################
for each in Res_ids:
    values=Res[each]
    table="sensor.bed_raw_"+str(each)+"_only"
    #####################################################################################################
    ########## LOOPING THROUGH EACH ID, EACH DATE and ITS DATA and PROCESS IN BLOCKS OF 2 HRS ###########
    #####################################################################################################
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   Starting ID:  ", each,"   %%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    for each_date in values:
        print("######################### Beginning Date:  ", each,"   ", each_date,"   #########################")
        Res_ID=each
        print(each,each_date)
        ########### DATES PROCESSING ######################
        Start=each_date+" 00:00:00.00"
        Start = pd.to_datetime(Start)
        End = Start+datetime.timedelta(hours=24)
        Start_End_Directory=str(Start)+"_"+str(End)
        
        ########### DURATION OF START AND END ##############
        duration = End - Start
        duration_in_s = duration.total_seconds()
        ############# (2HRS * 60 * 60)sec * 100 data points/sec
        TIME_WINDOW_BATCH = 7200.0 # Time Window of data that we can pull from database. We can't pull24hrs data, so I am pulling data in batches and then process it with a processing time window.

        # Choice of processing or slicing time window in a batch of 2hrs.
        TIME_WINDOW = 60 
        print(duration_in_s,TIME_WINDOW_BATCH)
        
        #####################################################################################################
        ################################### RESULT FOLDER PATH ##############################################
        #####################################################################################################
        Path = "/home/pg3fy/jupyter/IR/COPD/NEW_WORK_For_IE_Ratio_AND_FeatureExtraction_AND_Clustering_PythonPeakDetection/RESULTS_FROM_CLEANED_SCRIPT/"
        if (duration_in_s > TIME_WINDOW_BATCH):
            i=Start
            while(i<End):
                Sub_End=pd.to_datetime(i + pd.to_timedelta(TIME_WINDOW_BATCH, unit='s'))
                
                #####################################################################################################
                ##### Provide Specifics to pull data from POSTGRES, preprocess, clean and Generate Features #########
                #####################################################################################################
                result=RunData(i,Sub_End,Res_ID,table,Start_End_Directory,TIME_WINDOW,Path)
                
                ##### Checking for empty data retrieved from postgres #####
                if(len(result) == 0):
                    i=Sub_End
                    continue
                else:      
                    i=Sub_End
                    time.sleep(2)    
        else:
            #result=RunData(Start,End,Res_ID,table,Start_End_Directory,TIME_WINDOW,Path)
            RunData(Start,End,Res_ID,table,Start_End_Directory,TIME_WINDOW,Path)
        file1.write(str(Start)+"\n")
        
        print("######################### Done Date:  ",each,"  ",each_date,"   #########################")
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   Done ID:  ", each,"   %%%%%%%%%%%%%%%%%%%%%%%%%%%%")

###### SCRIPT RUN STATUS FILE:Close the file ######
file1.close()
