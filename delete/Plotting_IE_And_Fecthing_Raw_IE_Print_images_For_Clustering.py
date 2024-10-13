from matplotlib.pyplot import *
import matplotlib.pyplot as plt
from scipy import stats
from matplotlib.backends.backend_pdf import PdfPages
import statistics
import matplotlib.pyplot as plt
from scipy.misc import electrocardiogram
from scipy.signal import find_peaks
import os,sys
import pandas as pd
import numpy as np
from Get_IE_Ratio import Calculate_IE_Ratio
from HouseKeepingFunctions import CheckFileExistence
from Get_Shannon_Entropy import ShannonEntropy
from ExtractPeakToPeakFeatures import Calculate_Breath_To_Breath_Features

def CreateDirectory(MYDIR):
    CHECK_FOLDER = os.path.isdir(MYDIR)

    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(MYDIR)
        print("created folder : ", MYDIR)

    else:
        print(MYDIR, "folder already exists.")
        
def CleanNoise(Sigdata,MACRes,TIME_WINDOW,ResID,StartEndPath,ResultDir):
    Raw=dict()
    #Step1: Calling for IE Ratio
    df1=Calculate_IE_Ratio(MACRes['Res1'])
    BtoB1=Calculate_Breath_To_Breath_Features(MACRes['Res1'])
    #print(df1.head())
    df2=Calculate_IE_Ratio(MACRes['Res2'])
    BtoB2=Calculate_Breath_To_Breath_Features(MACRes['Res2'])
    #print(df2.head())
    df3=Calculate_IE_Ratio(MACRes['Res3'])
    BtoB3=Calculate_Breath_To_Breath_Features(MACRes['Res3'])
    #print(df3.head())
    df4=Calculate_IE_Ratio(MACRes['Res4'])
    BtoB4=Calculate_Breath_To_Breath_Features(MACRes['Res4'])
    #print(df4.head())
    #display(df.head())
    
    Sigdata['TimeStamp']=pd.to_datetime(Sigdata['TimeStamp'])
    #Plot_With_Data_And_IE_Ratio(Sigdata,MACRes,df,60,3054)
    x=df1.Start.min()
    plotIndex=0
    inx=1
    plot_x=dict()
    plot_2=dict()

    #Step 2: Create a directory for the resident
    #Path="IE_MACResults"
    Path=ResultDir
    CreateDirectory(Path)
    CreateDirectory(Path+"/"+str(ResID)+"/"+StartEndPath)
    
    ##FilePaths for pdf file for the plots
    filePath=Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
        str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+".pdf"
    IE_file=Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
        str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+"_IE_Ratio.csv"
    
    Features_file=Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
        str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+"_Features.csv"
    
    RAW_IE_file=Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
        str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+"RAW_IE_Ratio.csv"
    
    Shannon_file=Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
        str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+"_Shannon.csv"
    print(filePath)
    
    ImagesPath=Path+"/"+str(ResID)+"/"+StartEndPath+"/imagesBeforeClustering/"
    
    Features_Cluster_file=Path+"/"+str(ResID)+"/"+StartEndPath+"/"+\
        str(Sigdata.TimeStamp.min())+"_"+str(Sigdata.TimeStamp.max())+"Features_Cluster.csv"
    
    #filePath="test.pdf"
    #Check if the file exists
    if os.path.exists(filePath):
        os.remove(filePath)
    CheckFileExistence(IE_file)
    CheckFileExistence(Features_Cluster_file)
    CheckFileExistence(RAW_IE_file)
    CheckFileExistence(Features_file)
    CheckFileExistence(Shannon_file)
    CreateDirectory(ImagesPath)
    #After removing the previous file create new file    
    pdf = PdfPages(filePath) 
    
    Data=[]
    IE_details=[]
    #RAW_IE=[]   
    RAW_IE=pd.DataFrame()
    Features=[]
    Shannon=[]
    Features_Cluster=[]
    #Shannon
    ##Step 3:Run in a loop of time windows
    while x <= df1.End.max():
    
        #Raw=dict()
        first=x
        x=pd.to_datetime(x + pd.to_timedelta(TIME_WINDOW, unit='s'))
        #sub_res2=Sigdata[Sigdata["TimeStamp"].between(first,x)]
        sub_res2=Sigdata[(Sigdata["TimeStamp"] >= first) & (Sigdata["TimeStamp"]<=x)]
        
        
        # As per sample frequency 100 samples/sec there should be 
        #60*Minute*100 samples. Since we are using 3 minute window the
        # maximum number of samples should be 18000(60*3*100). We are just
        # limiting to a lower range observed in the data.
        NumFsCutOff = (TIME_WINDOW*100)-100
        if(sub_res2.shape[0]<NumFsCutOff):
            continue
            
        #Cleaning starts here
        #Step 3.1: Select the best transducer
        #print(">>>>>>>>>>>>>>>>>>>>> SSTTAARRTT >>>>>>>>>>>>>>",)
        Raw[1]=sub_res2['raw1'].sum()
        Raw[2]=sub_res2['raw2'].sum()
        Raw[3]=sub_res2['raw3'].sum()
        Raw[4]=sub_res2['raw4'].sum()
        max_key = max(Raw, key=Raw.get) #GET THE BEST TRANSDUCER NUMBER
        BestTransducerSelect="butterf"+str(max_key) #GET THE BEST TRANSDUCER NAME+NUMBER
        
        #Step 3.2: Select the best transducer
        MAC_BestTransducer = MACRes['Res'+str(max_key)]
        sub_MAC_BestTransducer=MAC_BestTransducer\
            [(MAC_BestTransducer["resp_pv_dt_IE"] >= first) & (MAC_BestTransducer["resp_pv_dt_IE"]<=x)]
            #MAC_BestTransducer[MAC_BestTransducer["resp_pv_dt_IE"].between(first,x)]
        #sub_MAC_BestTransducer=MACRes[MACRes["resp_pv_dt_IE"].between(first,x)]
        #resp_pv_dt_IE
        #print((df.Start.min(), ">=", first, df.End.max(),"<=", x))
        #print("MAX KEY ",max_key) 
        if (max_key==1): 
            Sub_MAC_IE=df1[(df1['Start'] >= first) & (df1['End']<=x)]
            Sub_B2B=BtoB1[(BtoB1['Start'] >= first) & (BtoB1['End']<=x)]
            #print(Sub_MAC_IE.shape[0],Sub_B2B.shape[0],min(Sub_MAC_IE['Start'].to_list),min(Sub_MAC_IE.shape['Start'].to_list))
        elif(max_key==2): 
            Sub_MAC_IE=df2[(df2['Start'] >= first) & (df2['End']<=x)]
            Sub_B2B=BtoB2[(BtoB2['Start'] >= first) & (BtoB2['End']<=x)]
            #print(Sub_MAC_IE.shape[0],Sub_B2B.shape[0],min(Sub_MAC_IE['Start'].to_list),min(Sub_MAC_IE.shape['Start'].to_list))
        elif(max_key==3): 
            Sub_MAC_IE=df3[(df3['Start'] >= first) & (df3['End']<=x)]
            Sub_B2B=BtoB3[(BtoB3['Start'] >= first) & (BtoB3['End']<=x)]
            #print(Sub_MAC_IE.shape[0],Sub_B2B.shape[0],min(Sub_MAC_IE['Start'].to_list),min(Sub_MAC_IE.shape['Start'].to_list))
        elif(max_key==4):
            Sub_MAC_IE=df4[(df4['Start'] >= first) & (df4['End']<=x)]
            Sub_B2B=BtoB4[(BtoB4['Start'] >= first) & (BtoB4['End']<=x)]
            #print(Sub_MAC_IE.shape[0],Sub_B2B.shape[0],min(Sub_MAC_IE['Start'].to_list),min(Sub_MAC_IE.shape['Start'].to_list))
    
        
        
    
        #Step 3: Get the data custom window
        #if not (sub_MAC_BestTransducer["resp_pv_vals"].isnull().values
        """
        #EXCLUDE APNEA AND HYPOPNEA WINDOWS
        #if(33 in sub_MAC_BestTransducer.resp_pvs.values or -33 in sub_MAC_BestTransducer.resp_pvs.values):
        #    continue
            
        #EXCLUDING THE Windows with missing data or NAN.    
        #elif not (sub_MAC_BestTransducer["resp_pv_vals"].isnull().values.any()):
        if not (sub_MAC_BestTransducer["resp_pvs"].isnull().values.any()):
            continue
            Data.append([str(inx),first,x,sub_res2[BestTransducerSelect].to_list()])
            
            
   
            #Features>>>>>>>>>>>>>>>>>>>>I_E Starts>>>>>>>>>>>>>>>>>>>>>>>>>>>  
            MACResp_Rate_per_minute=len(Sub_MAC_IE['I_E'].to_list())
            Normal_IE=len(list(x for x in Sub_MAC_IE['I_E'].to_list() if 0.3 <= x <= 0.6)) # I:E between 0.3 to 0.6
            Below_03=len(list(x for x in Sub_MAC_IE['I_E'].to_list() if x < 0.3)) # I:E between 0.3 to 0.6
            Bet_06_to_09=len(list(x for x in Sub_MAC_IE['I_E'].to_list() if 0.6 < x <= 0.9)) # I:E between 0.3 to 0.6
            At_1=len(list(x for x in Sub_MAC_IE['I_E'].to_list() if x==1.0))
            Greaterthan_1=len(list(x for x in Sub_MAC_IE['I_E'].to_list() if x>1.0))
            if((Normal_IE==0) or (MACResp_Rate_per_minute==0)):
                Normal_IE_Ratio_PerMin=0 
                Var_valley=0#1                        
                Var_I_E=0                                    
                Var_I_only=0       
                Var_E_only=0
                Var_I_by_Total=0         
                Var_Total_IE=0
                Var_Diff_IE=0
                percentageIE=0        
                Resp_Rate_per_minute=0
                p_Shannon=0
                v_Shannon=0
                
            #MACResp_Rate_per_minute=len(Sub_MAC_IE['I_E'].to_list())
            #Normal_IE=len(list(x for x in Sub_MAC_IE['I_E'].to_list() if 0.3 <= x <= 0.6))
            Normal_IE_Ratio_PerMin=round((Normal_IE/MACResp_Rate_per_minute),2)
            if Normal_IE_Ratio_PerMin >=0.60:
                Normal="Yes"
            else:
                Normal="No"
                #print(RAW_IE.tail(10))
        """        #print(Normal_IE,MACResp_Rate_per_minute,first,x,sub_MAC_BestTransducer["resp_pv_vals"].to_list(),len(sub_MAC_BestTransducer["resp_pv_vals"]))
            #elif((sub_MAC_BestTransducer[sub_MAC_BestTransducer['resp_pvs']==1]).shape[0]>2):
        if((len(Sub_MAC_IE['count'].to_list())>5) and Sub_B2B.shape[0]>5):
            print(Sub_MAC_IE['count'].to_list())
            MACResp_Rate_per_minute=len(Sub_MAC_IE['I_E'].to_list())
            Normal_IE=len(list(x for x in Sub_MAC_IE['I_E'].to_list() if 0.3 <= x <= 0.6))
            Normal_IE_Ratio_PerMin=round((Normal_IE/MACResp_Rate_per_minute),2)
            if Normal_IE_Ratio_PerMin >=0.60:
                Normal="Yes"
            else:
                Normal="No"
                
               
           ################################# FEATURES FROM RUHAN THESIS STARTS #############################
                
            #################################### Breath to Breath Features Starts #############################
            #print(Sub_B2B['Breath_to_Breath'].to_list())
            RMSSD_B2B = np.sqrt(np.mean(np.square(Sub_B2B['Breath_to_Breath'].to_list())))
            mDi_B2B = np.mean(Sub_B2B['Breath_to_Breath'].to_list())
            print("MAX", RMSSD_B2B, Sub_B2B['Breath_to_Breath'].to_list())
            Max_B2B = max(Sub_B2B['Breath_to_Breath'].to_list())
            Min_B2B = min(Sub_B2B['Breath_to_Breath'].to_list())
                
            RMSSD_B2B_diffInAmplitudes = np.sqrt(np.mean(np.square(Sub_B2B['Sucessive_BtoB_diffenceInAmplitudes'].to_list())))
            mDi_B2B_diffInAmplitudes = np.mean(Sub_B2B['Sucessive_BtoB_diffenceInAmplitudes'].to_list())
            Max_B2B_diffInAmplitudes = max(Sub_B2B['Sucessive_BtoB_diffenceInAmplitudes'].to_list())
            Min_B2B_diffInAmplitudes = min(Sub_B2B['Sucessive_BtoB_diffenceInAmplitudes'].to_list())
                
                
            RMSSD_B2B_diffInHeights = np.sqrt(np.mean(np.square(Sub_B2B['Sucessive_BtoB_diffenceInHeights'].to_list())))
            mDi_B2B_diffInHeights = np.mean(Sub_B2B['Sucessive_BtoB_diffenceInHeights'].to_list())
            Max_B2B_diffInHeights = max(Sub_B2B['Sucessive_BtoB_diffenceInHeights'].to_list())
            Min_B2B_diffInHeights = min(Sub_B2B['Sucessive_BtoB_diffenceInHeights'].to_list())
                     
                
            #################################### Breath to Breath Features Ends ##############################
                
            ################################### WIthin Breath Features Starts ################################
            #"Insp_diff_in_amplitudes","Exp_diff_in_amplitudes","ht","Diff_In_Valley_amplitudes"
            Var_I_only=statistics.variance(Sub_MAC_IE['I_only'].to_list()) 
            Var_E_only=statistics.variance(Sub_MAC_IE['E_only'].to_list())          
            Var_I_by_Total=round((statistics.variance(Sub_MAC_IE['I_by_Total'].to_list())),2)          
            Var_Total_IE=statistics.variance(Sub_MAC_IE['Total_IE'].to_list())
            Var_Diff_IE=statistics.variance(Sub_MAC_IE['Diff_IE'].to_list())
            percentageIE=round(((Normal_IE/MACResp_Rate_per_minute)*100),2)          
            Resp_Rate_per_minute=len(Sub_MAC_IE['I_E'].to_list())
            print(Sub_MAC_IE['Insp_diff_in_amplitudes'].to_list()) 
            Amp_I=np.mean(Sub_MAC_IE['Insp_diff_in_amplitudes'].to_list())
            Amp_E=np.mean(Sub_MAC_IE['Exp_diff_in_amplitudes'].to_list())
                    
            Ratio_MD_Amp=Amp_I/Amp_E
            Ratio_RMSD_Amp=(np.sqrt(np.mean(np.square(Sub_MAC_IE['Insp_diff_in_amplitudes'].to_list()))))/(np.sqrt(np.mean(np.square(Sub_MAC_IE['Exp_diff_in_amplitudes'].to_list()))))
            Max_Amp_I=max(Sub_MAC_IE['Insp_diff_in_amplitudes'].to_list())
            Min_Amp_I=min(Sub_MAC_IE['Insp_diff_in_amplitudes'].to_list())
            Diff_Max_Min_I = Max_Amp_I-Min_Amp_I
                
            Max_Amp_E=max(Sub_MAC_IE['Exp_diff_in_amplitudes'].to_list())
            Min_Amp_E=min(Sub_MAC_IE['Exp_diff_in_amplitudes'].to_list())
            Diff_Max_Min_E = Max_Amp_I-Min_Amp_I
                
            RMI=np.mean(Sub_MAC_IE['I_only'].to_list())/np.mean(Sub_MAC_IE['E_only'].to_list())
                
                
            ################################### WIthin Breath Features Ends ################################
                
            Features_Cluster.append([str(first)+"_"+str(x),RMSSD_B2B,mDi_B2B,Max_B2B,Min_B2B,RMSSD_B2B_diffInAmplitudes,mDi_B2B_diffInAmplitudes, Max_B2B_diffInAmplitudes, Min_B2B_diffInAmplitudes, RMSSD_B2B_diffInHeights, mDi_B2B_diffInHeights,\
                Max_B2B_diffInHeights, Min_B2B_diffInHeights,Var_I_only, Var_E_only, Var_I_by_Total, Var_Total_IE, \
                Var_Diff_IE, percentageIE, Resp_Rate_per_minute, Ratio_MD_Amp, Ratio_RMSD_Amp, \
                                         Diff_Max_Min_I, Diff_Max_Min_E, RMI,Normal_IE_Ratio_PerMin,Normal])
                
            ################################# FEATURES FROM RUHAN THESIS ENDS #############################
          
            """
                Var_I_E=round(statistics.variance(Sub_MAC_IE['I_E'].to_list()),2)                
                #print("Var_Total_IE:",Sub_MAC_IE['Total_IE'].to_list())          
                #print("Var_I_only:",Sub_MAC_IE['I_only'].to_list())           
                #print("Var_E_only:",Sub_MAC_IE['E_only'].to_list())          
                #print("Var_I_by_Total:",Sub_MAC_IE['I_by_Total'].to_list())                           
                Var_I_only=statistics.variance(Sub_MAC_IE['I_only'].to_list())           
                Var_E_only=statistics.variance(Sub_MAC_IE['E_only'].to_list())          
                Var_I_by_Total=round((statistics.variance(Sub_MAC_IE['I_by_Total'].to_list())),2)          
                Var_Total_IE=statistics.variance(Sub_MAC_IE['Total_IE'].to_list())
                Var_Diff_IE=statistics.variance(Sub_MAC_IE['Diff_IE'].to_list())
                percentageIE=round(((Normal_IE/MACResp_Rate_per_minute)*100),2)          
                Resp_Rate_per_minute=len(Sub_MAC_IE['I_E'].to_list())
                #Shannon.append([Sub_MAC_IE['Start'].min(),Sub_MAC_IE['Start'].max(),p_Shannon,v_Shannon])
                #Features.append([inx,Sub_MAC_IE['Start'],Sub_MAC_IE['Start'],Var_peaks,Var_valley,Var_I_E,Var_I_only,Var_E_only, Var_I_by_Total,Var_Total_IE,Var_Diff_IE,percentageIE,Resp_Rate_per_minute])
                
                """     
            # Features BUILDING STARTS HERE
            #Variance in I:E
         
            #IE_details.append([Normal_IE_Ratio_PerMin,MACResp_Rate_per_minute,Normal_IE,Below_03,Bet_06_to_09,At_1,Greaterthan_1,first,x,Sub_MAC_IE['I_E'].to_list()]) 
            #Features>>>>>>>>>>>>>>>>>>>>>END>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
             
            #**************************** PLOTTING BEGINS HERE ********************************
            #**************************** PLOTTING BEGINS HERE ********************************
            ### PLOT REGULAR DATA
            #Data for first Plot
            plot_x[plotIndex]=sub_res2[BestTransducerSelect].to_list()
            
            fig = plt.figure(figsize=(12,4))    # This line is needed for outputting the plot into pdf
            #plt.subplot(1, 3, 1) WIth three plots
            plt.subplot(1,2,1)
            plt.plot(plot_x[plotIndex])
            
            txt1 = "#   MACRespPeak_per_min=>"+str(MACResp_Rate_per_minute)
            txt = str(Normal_IE_Ratio_PerMin)+" RR:"+txt1+" "+Normal
            #plt.text(0.20,1.015,txt, transform=fig.transFigure, size=12,weight="bold")
    
            txt2="Cycle "+str(inx)+"_"+str(TIME_WINDOW)+"(sec) "+str(first)+"_"+str(x)
            plt.text(0.05,0.96,txt+"#"+txt2, transform=fig.transFigure, size=12)
    
            
            plt.xlabel('Samples in '+str(TIME_WINDOW)+'(sec)')
            plt.ylabel('Pressure signals')
            
            ### Plotting MAC
            #fig = plt.figure() 
            plot_x[plotIndex+1]=sub_MAC_BestTransducer['resp_pv_vals'].to_list()
            plt.subplot(1, 2, 2)
            plt.plot(plot_x[plotIndex+1])
            #plt.title("MAC_Filtered_"+title+"resp_pv_vals")
            plt.title("MAC S(P):")
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
            #**************************** PLOTTING ENDs HERE ********************************
        #numLab=numLab+1
            
        #print("DONE WITH ITERATION:", numLab)
        #break      
    pdf.close() #Comment it if plots are not opted for
    
    dfx=pd.DataFrame(Data,columns=['CycleIndex','StartTime','EndTime','SignalValuesinWindow'])
    
    #IE_Cols=["Normal_IE_Ratio_PerMin","MACResp_Rate_per_minute","Normal_IE(0.3-0.6)","Below_03","Bet_06_to_09","At_1","Greaterthan_1","first","x","IE_Ratio_List"] 
    #IE_df=pd.DataFrame(IE_details,columns=IE_Cols)
    #IE_df.to_csv(IE_file,index=False)
    
    #Shannon_Cols=["Start","End","p_Shannon","v_Shannon","Normal_IE_Ratio_PerMin","MACResp_Rate_per_minute"]
    #Shannon_df=pd.DataFrame(Shannon,columns=Shannon_Cols)
    #Shannon_df.to_csv(Shannon_file,index=False)
    
    Features_Cluster_Cols=["Start_End",'RMSSD_B2B','mDi_B2B','Max_B2B','Min_B2B','RMSSD_B2B_diffInAmplitudes','mDi_B2B_diffInAmplitudes',\
                'Max_B2B_diffInAmplitudes', 'Min_B2B_diffInAmplitudes', 'RMSSD_B2B_diffInHeights', 'mDi_B2B_diffInHeights',\
                'Max_B2B_diffInHeights', 'Min_B2B_diffInHeights','Var_I_only', 'Var_E_only', 'Var_I_by_Total', 'Var_Total_IE', \
                'Var_Diff_IE', 'percentageIE', 'Resp_Rate_per_minute', 'Ratio_MD_Amp', 'Ratio_RMSD_Amp', \
                                         'Diff_Max_Min_I', 'Diff_Max_Min_E', 'RMI','Normal_IE_Ratio_PerMin','Normal']
    
    FeaturesCluster=pd.DataFrame(Features_Cluster,columns=Features_Cluster_Cols)
    #Features_Cluster_Cols.to_csv(FeaturesCluster,index=False)
    FeaturesCluster.to_csv(Features_Cluster_file,index=False)
    
    #Features.append([Var_peaks,Var_valley,Var_I_E,Var_I_only,Var_E_only, Var_I_by_Total,Var_Total_IE,Var_Diff_IE,percentageIE,Resp_Rate_per_minute])
    #Features_Col=['CycleIndex','StartTime','EndTime','Var_peaks', 'Var_hts', 'Normal_IE_Ratio_PerMin','MACResp_Rate_per_minute','Var_IE']
    #Features_df=pd.DataFrame(Features,columns=Features_Col)
    #Features_df.to_csv(Features_file,index=False)
    
    if(RAW_IE.shape[0]>1):
        RAW_IE.to_csv(RAW_IE_file,index=False)
    return(dfx)
    
