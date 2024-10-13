### What is the script about? Either write here or the some where else in the readme.
Original Sorce: https://europa.dsa.missouri.edu/user/pg3fy/notebooks/IR/COPD/NEW_WORK_For_IE_Ratio_AND_FeatureExtraction_AND_Clustering_PythonPeakDetection/Perform%20Clustering%20Experiments-RuhanFeatures-3054Only-Functionalized-TestFiltering(FINAL%20RIGHT).ipynb
TryRunAndAddIntoGithub: https://europa.dsa.missouri.edu/user/pg3fy/notebooks/IR/COPD/NEW_WORK_For_IE_Ratio_AND_FeatureExtraction_AND_Clustering_PythonPeakDetection/Perform%20Clustering%20Experiments-RuhanFeatures-3054Only-Functionalized-TestFiltering(FINAL%20RIGHT)-Copy1.ipynb

########################################################
############### Regular Python Packages ################
########################################################
import os,sys
import numpy as np
import pandas as pd
from glob import glob
#from ggplot import *
from scipy import stats
from collections import Counter
from matplotlib.backends.backend_pdf import PdfPages

## ggplot
from rpy2.robjects import r
from rpy2.robjects.lib import ggplot2
from rpy2.robjects.packages import importr

## import more plot libraries using plotnine
from plotnine.data import mpg
from plotnine import ggplot, aes, labs, geom_point, geom_line, geom_bar, facet_grid, facet_wrap, theme

########################################################
######## Self Built Functions Import Begins Here# ######
########################################################
sys.path.append("DataMergeAndMining/")
sys.path.append("DataPreprocessingAndFeatureExtraction/")

from HouseKeepingFunctions import CheckFileExistence,CreateDirectory
from PerformClusteringFunctions import Specific_Names, Get_All_csv_pathnamesWithPatterns, Get_All_csv_pathnames, Get_All_png_pathnames, ProcessResultFilesForPyramids, PlotByDate, SubsetDataShannon, GetUnique_Dates, nested_dict, Get_Single_Way_Counted_with_CutOff, Get_Both_Way_Counted_with_CutOff, GiveFeaturesToBeCountedAndCutOff, TestKmeans, ApplyKmeans, RemoveAllFilesInADirectory, CopyFiles, getVariantFeatures, GeneratePlotsForFeatures, GeneratePlotsIntoApdfForFeatures, printConfusionMatrixAndReport, buildBoxPlot, buildBoxPlotWithGroupBy, buildBoxPlotWithGroupBySeperately, UniqueOfLabel, getDataFeaturesStatistics, CallTNSE, PlotStatsForLabelClusters, getVaryingData, CombineData, ApplyDBSCAN, shuffleLabelAsPerDescRespRate, PlotStatsForLabelClusters, getVariantFeatures

#print(pd.__version__)
#print(np.__version__)

scales = importr('scales')

#####################################################################################################
########## Function to Merge the feataures from date wise extracted and stored features #############
#####################################################################################################

def getVariantFeatures(df_dataa):
    #####################################################################################################
    ############################## Name of the Features To be Imported ##################################
    #####################################################################################################
    Features_Cluster_Cols=['Ru_mDI','Ru_RespRate','Ru_RMSSD','Ru_MADI','Ru_RMI','Ru_RMDA_RMS','Restlessness3Sec','NAsign',\
                          'A_Mean_i','A_Mean_e','ht_Mean_av','ht_Mean_max','ht_RMS_av','ht_RMS_max','Ru_A_RMSi','Ru_A_RMSe']


    #####################################################################################################
    ############################## Name of the Features To be Imported ##################################
    #####################################################################################################
    #target=df_data['Target'].to_list()
    Index=df_dataa['Start_End'].to_list()
    df_dataa=df_dataa.drop(columns=['Start_End'])
    df_dataa['Normal'].replace(['Yes', 'No'],[1, 0], inplace=True)
    
    VariantFeatures=[]
    for i in Features_Cluster_Cols:
        if i=="NAsign":  #
            VariantFeatures.append(i)#
            continue #
        print(i," ",df_dataa[i].var())
        if(df_dataa[i].var()>0.5):
            VariantFeatures.append(i)

    df_variant = df_data[VariantFeatures]
    print(df_variant.shape)
    display(df_variant.head())
    df_variant=df_data[Features_Cluster_Cols]
    return(df_variant)



import matplotlib.pyplot as plt
import datetime
import os

#####################################################################################################
#####################################################################################################
########### Extract Features With Specific Resident IDs (For Certain Dates and Columns)##############
#####################################################################################################
#####################################################################################################

IndexFilePath='/dsa/home/pg3fy/jupyter/IR/COPD/NEW_WORK_For_IE_Ratio_AND_FeatureExtraction_AND_Clustering_PythonPeakDetection/\
PlottingCombined/Predictions_WithoutNoise_WithBPI/'
CreateDirectory(IndexFilePath)
#####################################################################################################
#Step 1:List of resident IDs whose for whom features are to be used for data mining and preictions later on
#####################################################################################################
Ids=['6219','6115','3121','3054', '3083','3127','3104']

Extension=".csv"
pp='/home/pg3fy/jupyter/IR/COPD/NEW_WORK_For_IE_Ratio_AND_FeatureExtraction_AND_Clustering_PythonPeakDetection/' #Whole
#MainPath=pp+'Features_MACResults_TestingPeakDetect_WithoutImages_AmplitudeTest_ProminenceTest/'
##MainPath=pp+'Features_MACResults_TestingPeakDetect_WithoutImages_AmplitudeTest_ProminenceTest_WithHeight/' ######

######## MainPath=pp+'COPD_IndexProgressionExperimentalDates/' #COPD INdex
#MainPath=pp+'Features_MACResults_TestingPeakDetect_WithoutImages_AmplitudeTest_ProminenceTest_WithNoiseCancellation/'
PlotFilePath=MainPath+'Summed_Plots.pdf'
if os.path.exists(PlotFilePath):
    os.remove(PlotFilePath)

######## After removing the previous file create new file
df_data=pd.DataFrame()
#####################################################################################################
#Step 2: Get all the unique dates for which data is available in each IDs. That is why creating a dict of {ID:[dates]}. 
######## This is step was required because the features extracted were stored datewise in folders for future references
#####################################################################################################
Date_dict=dict()
for i in Ids:
    path=MainPath+i+"/"
    All_Files=Get_All_csv_pathnames(path)
    df_data=pd.DataFrame()
    Date_dict[i]=GetUnique_Dates(All_Files)
    
print(Date_dict)    

#####################################################################################################
#Step 3: Get all the features for all the days/dates for each resident and put them in ONE DATAFRAME
#_Features (df_data)
#####################################################################################################

SummedData=[]
df_Comb=pd.DataFrame()
for IDs in Date_dict.keys():
    print("id",IDs)
    ##############################################
    ####### Looping through each date in each ID
    ##############################################
    for eachDate in list(Date_dict[IDs]):
        #print(eachDate)
        path=MainPath+IDs+"/"
        All_Files=Get_All_csv_pathnames(path)
        print("****************ID ",IDs,eachDate," begins here*****************")
        
        df_data=pd.DataFrame()
        df_filtered=pd.DataFrame()

        #######################################################################################################
        ####### Looping through each file with eachdate in each ID making ONE COMBINED FEATURE FILE FOR EACH ID
        #######################################################################################################
        for eachfile in All_Files:
            if ((eachDate in eachfile) and (str(IDs) in eachfile) and (eachfile.endswith(FilenameEnding))):
                GetData=ProcessResultFilesForPyramids(eachfile,IDs)
                if(len(GetData)>0):
                    #df_data is One COMBINED FEATURE FILE for EACH ID for ALL Dates
                    df_data=df_data.append(ProcessResultFilesForPyramids(eachfile,IDs))
        
        ### Form UNIQUE INDEX for each 60 sec window  using the start_end column (having starting and ending timestamps)
        Index=df_data['Start_End'].to_list()

        #######################################################################################################
        ####### Build a subset data with the relevant features mentioned in function getVariantFeatures() #####
        ######################### df_data(full set) =>  df_Comb (subset of features)###########################
        df_Mid=pd.DataFrame()
        df_Mid=getVariantFeatures(df_data)
        df_Mid['Index']=df_data['Start_End']
        #df_3083['target']=1
        df_Mid['ID']=IDs
        df_Mid['Date']=eachDate
        df_Comb=df_Comb.append(df_Mid)

######################################################################################################
# STEP 4: ################################### DROPPING NOISY WINDOWS #####################################
#### Also this is a step to extract a statistics on Noisy 60 sec window percentages in each datase ###
######################################################################################################
NA=pd.DataFrame()

##NAsign columns contains 'Yes' if it is noisy windows and 'no' if not
NA=df_Comb[df_Comb['NAsign']=='yes']
NotNA=df_Comb.shape[0]-NA.shape[0]
print("NA: ",NA.shape[0],"\n","NotNA",NotNA,"\n","Total",df_Comb.shape[0])
NA['ID']=NA['ID'].astype(str)

print(NA.dtypes)
for listIDs in Ids:
    if NA['ID'].str.contains(listIDs).any():
        NA_count=pd.DataFrame()
        NA_count=NA[NA['ID']==listIDs]
        print(listIDs," => Number of windows with noise:",NA_count.shape[0])

######################################### DROPPING NOISY WINDOWS #####################################        
if Noise=="Drop":
    df_Comb=df_Comb[df_Comb['NAsign']=='no'] 
df_Comb=df_Comb.drop(columns=['NAsign'])#,'Restlessness3Sec'])
#DROPPING NOISY WINDOWS ENDS

######################################################################################################
# STEP 5: ################# Further merging and normalizing features #################################
#### (a)Normalizing restlessness feature, and (b) Calulating BPI feature by combining two features ###
######################################################################################################

#### (a)Normalizing restlessness feature
NA['Restlessness3Sec']=NA['Restlessness3Sec']/60
NA['Restlessness3Sec']=NA['Restlessness3Sec'].round()
print(NA['Restlessness3Sec'].mean())

#### (b)Calulating BPI feature by combining two features
df_Comb['BPI_ht_Mean_max']=df_Comb['Ru_RespRate']/df_Comb['ht_Mean_max']

######################################################################################################
### Step 6: #################### Store extracted features for all the IDs and dates into a file ######
######################################################################################################
df_Comb.to_csv('ExtractedFeatureFile.csv')
        
