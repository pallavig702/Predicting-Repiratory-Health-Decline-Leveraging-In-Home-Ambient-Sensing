import math
import statistics
import numpy as np
import pandas as pd


def Calculate_IE_Ratio(data):
    data['resp_pv_dt_IE'] = pd.to_datetime(data['resp_pv_dt_IE'])
    i=0
    Resp_Cycle=1
    
    r_pvs = data['resp_pvs'].to_list()
    r_vals = data['resp_pv_vals'].to_list()
    r_hts = data['resp_pv_hghts'].to_list()
    r_time = data['resp_pv_dt_IE'].to_list()
    
    I_E=[]
    Start=[]
    End=[]
    I_only=[]
    E_only=[]
    I_by_Total=[]
    Total_IE=[]
    Total_IE2=[]
    Diff_IE=[]
    count=[]
    Insp_diff_in_amplitudes=[]
    Exp_diff_in_amplitudes=[]
    ht=[]
    Diff_In_Valley_amplitudes=[]
    numo=0
    while(i<data.shape[0]-4):
        #print(i)
    
        if((r_pvs[i]==-1) and r_pvs[i+1]==1 and r_pvs[i+2]==-1):
            #print(r_pvs[i],r_pvs[i+1],r_pvs[i+2])
            #print(r_vals[i],r_vals[i+1],r_vals[i+2])
            #print(r_hts[i],r_hts[i+1],r_hts[i+2])
            #print(r_time[i],r_time[i+1],r_time[i+2])
            
            I=(r_time[i+1]-r_time[i]).total_seconds()
            E=(r_time[i+2]-r_time[i+1]).total_seconds() # Skipped milli seconds because a lag is expected
            if((I==0) and (E==0)):
                    continue        
            
            if numo==0:
                print("From Get IE Ratio Script")
                print(r_time[i])
                print("From Get IE Ratio Script")
            numo=numo+1
            
            I_E.append(round((I/E),1))
            I_only.append(I)
            E_only.append(E)
            I_by_Total.append((round((I/(I+E)),2)))
            Total_IE.append(round((I+E),2))
            Total_IE2.append(r_time[i+2]-r_time[i])
            Diff_IE.append((E-I))
            #print(">>IE",I,E)
            #print(I_E)#,I,E)
            Insp_diff_in_amplitudes.append(r_vals[i+1]-r_vals[i])
            Exp_diff_in_amplitudes.append(r_vals[i+1]-r_vals[i+2])
            ht.append(r_hts[i+1])
            Diff_In_Valley_amplitudes.append(r_vals[i+2]-r_vals[i])
            
            Resp_Cycle=Resp_Cycle+1
            i=i+2
            #if(i==data.shape[0]-3):
            #print(i,i+2,data.shape[0],len(r_time))
            Start.append(r_time[i])
            End.append(r_time[i+2])
            count.append(1) #count of normal peaks exclusing apnea peaks with label 0
        else:
            i=i+1
  
    d = {'Start':Start,'End':End,'I_E':I_E,'I_only':I_only,'E_only':E_only,
         'I_by_Total':I_by_Total,'Total_IE':Total_IE,'Total_IE2':Total_IE2,'Diff_IE':Diff_IE,"count":count,"Insp_diff_in_amplitudes":Insp_diff_in_amplitudes,"Exp_diff_in_amplitudes":Exp_diff_in_amplitudes,"ht":ht,"Diff_In_Valley_amplitudes":Diff_In_Valley_amplitudes}
    df = pd.DataFrame(d)

    return(df)
