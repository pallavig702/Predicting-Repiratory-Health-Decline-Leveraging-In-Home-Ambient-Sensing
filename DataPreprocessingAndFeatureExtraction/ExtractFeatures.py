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

#from scipy.misc import electrocardiogram
#from Get_IE_Ratio import Calculate_IE_Ratio

########################################################
######## Self Built Functions Import Begins Here# ######
########################################################
from ExtractValleyToValleySignals import ExtractSignals
from ExtractValleyToValleySignals2 import ExtractSignals2

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
    
    #########################################################################
    ##STEP 1: GETTING SOME INITIALIZATIONS AND PREPROCESSING DONE ###########
    ######################################################################### 
    Data=[]
    Features_Cluster=[]
    
    ############# GETTING MIN TIME IN TIMESTAMP In  ####################
    df1=Calculate_IE_Ratio(MACRes['Res1']) #Only to get the start aligned to previous
    #StartMin=GetMinTimeStampWhere_v1Pv2_Start(MACRes['Res1']) #Else this could be used as x
    
    Sigdata['TimeStamp']=pd.to_datetime(Sigdata['TimeStamp'])
    x=df1.Start.min()
    #print("THIS IS THE TIME STAMP")
    #print(df1.Start.min(),StartMin,Sigdata['TimeStamp'].min(),StartEndPath)
    #print(MACRes['Res1'])
    #exit(0)
    ############INITIALIZING FOR PLOTTING #####################
    plotIndex=0
    inx=1
    plot_x=dict()
    plot_2=dict()
    #V1_P_V2=pd.DataFrame()
    #V1_P_V2_MAC=pd.DataFrame()
    
    #########################################################################
    ##STEP 2: CREATING A RESULT DIRECTORY with 2hours start end time window##
    #########################################################################
    
    ############Creating of directories for output path############
    Path=ResultDir
    CreateDirectory(Path+"/"+str(ResID)+"/")
    CreateDirectory(Path+"/"+str(ResID)+"/"+StartEndPath)
    
    ############ File Path - to Output Signal Segmented Data ############
    SegmentedSignal_file = Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
            str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+"SegmentedSignal.csv"
    
    ############ FilePath - to Output Feature extracted for Clustering ############
    Features_Cluster_file = Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
            str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+"Features_Cluster.csv"
                                             
    ############ File Path IMAGES BEFORE CLUSTERING _ FOR PNG FILES ############
    ImagesPath=Path+"/"+str(ResID)+"/"+StartEndPath+"/imagesBeforeClustering/"
    
    
    #########################################################################
    ##STEP 3: CHECKING FILE EXISTENCE ##
    #########################################################################
    
   ########## Checking File Existence ###########
    CheckFileExistence(SegmentedSignal_file)
    CheckFileExistence(Features_Cluster_file)
                                             
    #CheckFileExistence(V1_P_V2_file)
    #CheckFileExistence(V1_P_V2_MAC_file)
    
    ########## Creating Directory #############
    CreateDirectory(ImagesPath)
    
    ###################################################################################
    ##STEP 4: RUN IN A LOOP 2 HOURS TIME WINDOW TO GET 60-SEC TIME WINDOWS PROCESSED ##
    ###################################################################################
    ### For each time-window or epoch. Time window could be 30 or 60-second
                                             
    while x <= df1.End.max():
        Raw=dict() ## THIS WAS UNCOMMENTED #CHECK                                      
        first=x # start of the time window
        x=pd.to_datetime(x + pd.to_timedelta(TIME_WINDOW, unit='s')) #End of the time window
        
        #################################################################
        ##STEP 5: sub_res2 = CHOPPING THE TIME_WINDOW = 60-SEC WINDOW ###
        #################################################################
        sub_res2=Sigdata[(Sigdata["TimeStamp"] >= first) & (Sigdata["TimeStamp"]<=x)]
        
        
        ##############################################################################
        ## STEP 6: CHECKPOINT IF LESS THAN (TIME_WINDOW*100) DATA POINTS #############
        ##############################################################################
        ### DO NOT PROCESS the time windows with lesser number of data points ########
        # As per sample frequency 100 samples/sec there should be 
        #60*Minute*100 samples. Since we are using 3 minute window the
        # maximum number of samples should be 6000(60*100). We are just
        # limiting to a lower range observed in the data.
        NumFsCutOff = (TIME_WINDOW*100)-100
        if(sub_res2.shape[0]<NumFsCutOff):
            continue
            
        ######################################################################################
        ######## STEP 7: max_key=SELECTING THE BEST TRANSDUCER ###############################
        ######## BestTransducerSelect="butterb"+str(max_key) ## CHANGED HERE FOR BUTTER B ####
        ######################################################################################    
        Raw[1]=sub_res2['raw1'].sum()
        Raw[2]=sub_res2['raw2'].sum()
        Raw[3]=sub_res2['raw3'].sum()
        Raw[4]=sub_res2['raw4'].sum()
        max_key = max(Raw, key=Raw.get) #GET THE BEST TRANSDUCER NUMBER
        BestTransducerSelect="butterf"+str(max_key) #GET THE BEST TRANSDUCER NAME+NUMBER
        BestTransducerDCRemovedSelect="DC_Removed"+str(max_key)
        ###########################################################################
        ########################################################################
        ######## STEP 8: MAC_BestTransducer,FPeaks_BestTransducer ##############
        ######## SELECTING THE BEST TRANSDUCER SIGNAL SUBSET PEAKS #############
        ########################################################################
        
        MAC_BestTransducer = MACRes['Res'+str(max_key)]
        sub_MAC_BestTransducer=MAC_BestTransducer\
            [(MAC_BestTransducer["resp_pv_dt_IE"] >= first) & (MAC_BestTransducer["resp_pv_dt_IE"]<=x)]
        
        FPeaks_BestTransducer = FPeaks['P'+str(max_key)]
        sub_FPeaks_BestTransducer=FPeaks_BestTransducer\
            [(FPeaks_BestTransducer["resp_pv_dt_IE"] >= first) & (FPeaks_BestTransducer["resp_pv_dt_IE"]<=x)]
         
        ###############################################################################
        ###################### STEP 9: null values = noise ############################
        ######## Labeling THE NOISE WINDOWS - yes or no ###################
        ###############################################################################
       
        if sub_MAC_BestTransducer["resp_pv_vals"].isnull().values.any():
            NAsign="yes"
        else:
            NAsign="no"
                                             
        ##############################################################################################
        ########### STEP 10: CHECKPOINT: Dropping Dysfunctional/bad data Windows  ####################
        ######## Checking if number of peaks > 5, where the usual expectation is 12-18bpm ############
        ############################################################################################## 
        #if((len(Sub_MAC_IE['count'].to_list())>5) and Sub_B2B.shape[0]>5):
        
        #First CheckPoint
        NumPeaks = sub_FPeaks_BestTransducer[sub_FPeaks_BestTransducer['resp_pvs']==1] 
        if(NumPeaks.shape[0]<5 or len(sub_MAC_BestTransducer['resp_pv_vals'].to_list())<2):
            continue
        
        #Second CheckPoint
        var=statistics.variance(sub_MAC_BestTransducer['resp_pv_vals'].to_list())
        if ((len(sub_MAC_BestTransducer['resp_pvs'].to_list())<=3) & (var<=0.5)):
            continue
                                             
        ###############################################################################
        ##################  STEP 11: APPENDING SIGNAL DATA HERE ####################### 
        ######### Extracting the signals starting and ending at valleys ###################
        ####################################################################################   
        
        ###### old
        SignalV2V=ExtractSignals(sub_FPeaks_BestTransducer,sub_res2[BestTransducerSelect].to_list())
        '''
        Data.append([str(inx),first,x,SignalV2V,len(SignalV2V),(x-first).total_seconds()])
        print(sub_res2.head())
        ##### old
        
        #### new
        SignalV2V_2=ExtractSignals2(sub_FPeaks_BestTransducer,sub_res2[BestTransducerSelect].to_list(),sub_res2['TimeStamp'].to_list())
        #print("Out>>>>>>>>>",SignalV2V_2.head())
        #print("Out>>>>>>>>>",SignalV2V_2.head())
        Interpolated=pd.DataFrame()
        Interpolated=Interpolation(SignalV2V_2,"Signal")
        #print(SignalV2V_2.shape,Interpolated.shape)
        
        #exit(0)
        
        Data.append([str(inx),first,x,Interpolated['Signal'].to_list(),Interpolated.shape[0]])
        '''  #### new
        #Combination of new and old
        Interpolated=pd.DataFrame()
        Interpolated=Interpolation(sub_res2,BestTransducerSelect)
        InterpolatedDC_Removed=Interpolation(sub_res2,BestTransducerDCRemovedSelect)
        #Data.append([str(inx),first,x,Interpolated.shape[0],(x-first).total_seconds()])
        Sig=InterpolatedDC_Removed[BestTransducerDCRemovedSelect].to_list()
        #Sig=Interpolated[BestTransducerSelect].to_list()
        #print("Noise =>", NAsign)
        #print("Sig => ",Sig[0:100])
        #print("Pres Sig => ", Interpolated[BestTransducerSelect].to_list()[0:100])
        #exit(0)
        if len(Sig)==5999:
            #print(sum(my_dict['A'][-2:])/2)
            Sig.append(Sig[-1])
        elif len(Sig)==6001:
            Sig.pop()
        #print("hahahhahahahhahahsdgahsgfaksfga",len(Sig))
        Data.append([str(inx),first,x,Sig,len(Sig),(x-first).total_seconds()])
        #Data.append([str(inx),first,x,len(Sig),(x-first).total_seconds()])
                #Data.append([str(inx),first,x,ExtractSignals(sub_FPeaks_BestTransducer,sub_res2[BestTransducerSelect].to_list())])
       
        #Data.append([str(inx),first,x,sub_res2[BestTransducerSelect].to_list()])
        ###############################################################################
            
        ################################################################################
        ###################### STEP 12: CALCULATE RESTLESSNESS BEGINS ##################
        ################################################################################
        SubRestless=Restless[(Restless['starts_motion'] >= first) & (Restless['ends_motion']<=x)]
        test=pd.DataFrame()
        SRest=SubRestless.groupby('motion_strength_level')['motion_duration_in_second'].sum()
        #print(">>>>>>Restlessness>>>",SRest)
                                             
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

        ################################ CALCULATE RESTLESSNESS ENDS #############################
           
        #####################################################################################
        ########################## STEP 12:CALCULATE FEATURES  ###################
        ##################################################################################### 
        myFeatures=[]
        myFeatures=[str(first)+"_"+str(x),NAsign,Restlessness3Sec,Restlessness2Sec,Restlessness1Sec]  
        myFeatures.extend(Calculate_B_2_B_Features(sub_FPeaks_BestTransducer,\
        ImagesPath+str(first)+"_"+str(x)+".png"))

        sub=pd.DataFrame()
        sub=sub_FPeaks_BestTransducer[sub_FPeaks_BestTransducer['resp_pvs']==1]
        RespRate=len(sub['resp_pvs'].to_list())
        myFeatures.extend([RespRate])
       
        Features_Cluster.append(myFeatures)
        #####################################################################################
        
        '''
        #**************************** PLOTTING BEGINS HERE **********************************
        #####################################################################################
        ########################## STEP 12:Plot of Segmented windows   ######################
        ################ Plots of segmented windows are stored at ImagePath################## 
        #**************************** PLOTTING BEGINS HERE **********************************
        
        ### PLOT REGULAR DATA
        #Data for first Plot

        INDEXXX=[]
        indices=sub_FPeaks_BestTransducer['INDEX'].to_list()
        for COUNT, VALUES in enumerate(sub_FPeaks_BestTransducer['resp_pv_vals'].to_list()):
            if COUNT == 0:
                pos = sub_res2[BestTransducerSelect].to_list().index(sub_FPeaks_BestTransducer['resp_pv_vals'].to_list()[0])
                INDEXXX.append(pos)
            else:
                pos=pos+(indices[COUNT]-indices[COUNT-1])
                INDEXXX.append(pos)

        plot_x[plotIndex]=sub_res2[BestTransducerSelect].to_list()

        plot_x[plotIndex]=SignalV2V ## DELETE THIS NEW ADDITION FOR Plotting SignalV2V
        
        fig = plt.figure(figsize=(12,4))    # This line is needed for outputting the plot into pdf
        #plt.subplot(1, 3, 1) WIth three plots
        plt.subplot(1,2,1)
        plt.plot(plot_x[plotIndex])#,markevery=sub_FPeaks_BestTransducer['resp_pv_vals'].to_list())

        #plt.plot(5000,'g*')
        ##UNCOMMENT LINE BELOW 
        ##plt.scatter(INDEXXX, sub_FPeaks_BestTransducer['resp_pv_vals'].to_list(),marker=".")

        #txt1 = "#RespRate=>"+str(MACResp_Rate_per_minute)+"_"+str(RespRate)
        #txt = "I:E:"+str(Normal_IE_Ratio_PerMin)+" "+Normal
        #plt.text(0.20,1.015,txt, transform=fig.transFigure, size=12,weight="bold")

        txt2="Cycle "+str(inx)+"_"+str(TIME_WINDOW)+"(s) "+str(first)+"_"+str(x)+"_"
        plt.text(0.05,0.96,txt2, transform=fig.transFigure, size=12)

        plt.title("Restless:3,2,1:"+str(round(Restlessness3Sec,1))+","+str(round(Restlessness2Sec,1))+","+str(round(Restlessness1Sec,1)))
        plt.xlabel('Samples in '+str(TIME_WINDOW)+'(sec)')
        plt.ylabel('Pressure signals')

        ### Plotting MAC
        #fig = plt.figure() 
        plot_x[plotIndex+1]=sub_MAC_BestTransducer['resp_pv_vals'].to_list()
        plt.subplot(1, 2, 2)
        plt.plot(plot_x[plotIndex+1])
        #plt.title("MAC_Filtered_"+title+"resp_pv_vals")
        #plt.title("MAC:Prom"+str(round(RMS_Prom,2))+"_"+NA)
        plt.xlabel('Samples in '+str(TIME_WINDOW)+'(sec)')
        plt.ylabel('Pressure signals')
        plotIndex=plotIndex+2
        """
        ### PLOT REGULAR DATA
        #Data for first Plot
        plot_x[plotIndex]=sub_res2[BestTransducerSelect].to_list()

        fig = plt.figure(figsize=(12,4))    # This line is needed for outputting the plot into pdf
        plt.subplot(1, 3, 1)
        plt.plot(plot_x[plotIndex])

        Normal_I_ERatio = "#  Normal_I:E Ratio=>"+str(Normal_IE_Ratio_PerMin)
        txt1 = "#   MACRespPeak_per_min=>"+str(MACResp_Rate_per_minute)
        txt = "0.3 to 0.6 I:E=>"+str(Normal_IE)+txt1+Normal_I_ERatio
        #plt.text(0.20,1.015,txt, transform=fig.transFigure, size=12,weight="bold")

        txt2="Cycle "+str(inx)+"_"+str(TIME_WINDOW)+"(sec) "+str(first)+"_"+str(x)
        plt.text(0.05,0.96,txt+"#"+txt2, transform=fig.transFigure, size=12)

        plt.title("Low pass filtered samples")
        plt.xlabel('Samples in 60 seconds')
        plt.ylabel('Pressure signals')


        ### Plotting MAC
        #fig = plt.figure() 
        plot_x[plotIndex+1]=sub_MAC_BestTransducer['resp_pv_vals'].to_list()
        plt.subplot(1, 3, 2)
        plt.plot(plot_x[plotIndex+1])
        #plt.title("MAC_Filtered_"+title+"resp_pv_vals")
        plt.title("MAC S(P):"+str(p_Shannon)+" S(V):"+str(v_Shannon))
        plt.xlabel('Samples in 60 seconds')
        plt.ylabel('Pressure signals')

        # Plotting I:E Ratio per 60 sec
        #MACResp_Rate_per_minute=len(Sub_MAC_IE['I_E'].to_list())
        plot_x[plotIndex+2]=Sub_MAC_IE['I_E'].to_list()
        plt.subplot(1, 3, 3)
        plt.plot(plot_x[plotIndex+2])
        #plt.title("MAC_Filtered_"+title+"resp_pv_vals")
        plt.title("I:E Ratio plot for each peak in 60secs")
        plt.xlabel('Peaks in 60 sec')
        plt.ylabel('I:E Ratio')

        #plt.show()
        #pdf.savefig(fig) #THIS WAS COMMENTED TO PRINT FILES IN IMAGES
        plt.savefig(ImagesPath+str(first)+"_"+str(x)+".png") #NewAddition
        plt.cla() #New Addition
        plt.close(fig) #New Addition
        plotIndex=plotIndex+3
        inx=inx+1
        #**************************** PLOTTING ENDs HERE ********************************

        """
        plt.savefig(ImagesPath+str(first)+"_"+str(x)+".png") #NewAddition
        plt.cla() #New Addition
        plt.close(fig) #New Addition
        plotIndex=plotIndex+1

        inx=inx+1
        '''
        #**************************** PLOTTING ENDs HERE ********************************
    #numLab=numLab+1
        
    #print("DONE WITH ITERATION:", numLab)
    #break 
    #pdf.close() #Comment it if plots are not opted for
    ##UNCOMMENT HERE FOR SEPARATE IMAGES END
    
       
   
    # RAW SIGNAL VALUES EXTRACTION
    dfx=pd.DataFrame(Data,columns=['CycleIndex','StartTime','EndTime','SignalValuesinWindow','SigLen','SigTime'])
    #dfx=pd.DataFrame(Data,columns=['CycleIndex','StartTime','EndTime','SigLen','SigTime'])
    dfx.to_csv(SegmentedSignal_file,index=False)
    
    
    # FEATURES EXTRACTION
    Features_Cluster_Cols = ["Start_End","NAsign",'Restlessness3Sec','Restlessness2Sec','Restlessness1Sec','Ru_RMSSD','Ru_mDI','Ru_MADI','Ru_RespRate','Ru_SD_RR','Ru_RMDA','Ru_RMI','Ru_A_RMSi', 'Ru_A_RMSe', 'Ru_RMDA_RMS','A_Mean_i', 'A_Mean_e','ht_Mean_av','ht_Mean_max','ht_RMS_av','ht_RMS_max', 'A_inter_mean', 'A_inter_RMS', 'RespRateFromNewPeaks']
    FeaturesCluster=pd.DataFrame(Features_Cluster,columns=Features_Cluster_Cols)
    FeaturesCluster.to_csv(Features_Cluster_file,index=False)
    
    return(dfx)
