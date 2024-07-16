import os,sys
import pandas as pd
import numpy as np

####################################################################################################
########################### Check if the folders exits else create one #############################
####################################################################################################
def CreateDirectory(MYDIR):
    CHECK_FOLDER = os.path.isdir(MYDIR)

    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(MYDIR)
        print("created folder : ", MYDIR)

    else:
        print(MYDIR, "folder already exists.")
    
def Create_Multiple_Empty_pandas_dataframe(num):
    for i in range(num):
        x="Res"+str(i+1)
        #column_names = ["resp_pvs","resp_pv_vals","resp_pv_hghts","resp_pv_dt"]
        #exec('{} = pd.DataFrame(columns=column_names)'.format(x))
        exec('{} = pd.DataFrame(columns=column_names)'.format(x))

####################################################################################################
######### Check if the file exits before printing? If yes then delete and create fresh file ########
#################################################################################################### 
def CheckFileExistence(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)
        #print(Raw_IE_file," Created")
    #else:
    #    print("Can not delete the file as it doesn't exists")

def PrintIERatio(df,TransducerNumber,ResDir,ResID,StartEndPath):
    path=ResDir+"/"+str(ResID)+"/IE_Raw_Results/"
    CreateDirectory(path)
    CreateDirectory(path+"/T"+TransducerNumber+"/")
    Path=path+"/IE_Raw_Results/T"+TransducerNumber+"/"
    mini=df.Start.min()
    maxi=df.End.max()

    Raw_IE_file=Path+"/"+StartEndPath+"/"+str(mini)+"_"+str(maxi)+".csv"
    CheckFileExistence(Raw_IE_file)
    df.to_csv(Raw_IE_file,index=False)

def GetMinTimeStampWhere_v1Pv2_Start(data):
    data['resp_pv_dt_IE'] = pd.to_datetime(data['resp_pv_dt_IE'])
    
    i=0
    
    r_pvs = data['resp_pvs'].to_list()
    r_vals = data['resp_pv_vals'].to_list()
    r_hts = data['resp_pv_hghts'].to_list()
    r_time = data['resp_pv_dt_IE'].to_list()
    Start=[]
    while(i<data.shape[0]-4):
        if((r_pvs[i]==-1) and r_pvs[i+1]==1 and r_pvs[i+2]==-1):
            I=(r_time[i+1]-r_time[i]).total_seconds()
            E=(r_time[i+2]-r_time[i+1]).total_seconds() # Skipped milli seconds because a lag is expected
            if((I==0) and (E==0)):
                    continue
            Start.append(r_time[i])
            
            i=i+2
            #return(r_time[i])
        else: 
            i=i+1
    print(min(Start))
    return(min(Start))
