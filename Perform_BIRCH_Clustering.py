# Dendogram for Heirarchical Clustering

'''
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})

import time
#df_Comb=df_Comb.drop(columns=['Restlessness3Sec'])
i_dates='3054'#'3083'#

df_3054_1=df_Comb[df_Comb['ID']==i_dates]

IDdd=df_3054_1['ID'].to_list()
Index=df_3054_1['Index'].to_list()
dates=df_3054_1['Date'].to_list()
print(np.unique(dates))
df_3054_Clust=df_3054_1.drop(columns=['ID','Date','Index'])
df_3054_Clust.head()

import scipy.cluster.hierarchy as shc
import matplotlib
from matplotlib import pyplot

pyplot.figure(figsize=(10, 7))  
pyplot.title("Dendrograms")  
matplotlib.rcParams.update({'font.size': 22})

dend = shc.dendrogram(shc.linkage(df_3054_Clust, method='ward'))
'''

import time

i_dates='3054'#'3083'

df_3054_1=df_Comb[df_Comb['ID']==i_dates]

'''
ListOfIDs=['3054','6219']
#Filter the processed file for the IDs having COPD
boolean_series = df_Comb.ID.isin(ListOfIDs)
df_3054_1 = df_Comb[boolean_series]
'''

IDdd=df_3054_1['ID'].to_list()
Index=df_3054_1['Index'].to_list()
dates=df_3054_1['Date'].to_list()
print(np.unique(dates))
df_3054_Clust=df_3054_1.drop(columns=['ID','Date','Index'])
display(df_3054_Clust.head())

print("TOTAL DATAPOINTS",df_3054_Clust.shape[0])

number_Cluster=9

#TestKmeans(1,10,df_3054_Clust)
#kmComb=ApplyKmeans(df_3054_Clust,number_Cluster)

Resultpath="Result/"
LabelCount=Resultpath+'LabelCount.csv'
if os.path.exists(LabelCount):
    os.remove(LabelCount)
column_names=["0","1","2","3","4","date"]
#ApplyfuzzyCmeans
Label=[]
#Label=ApplyFuzzyCMenas(df_3054_Clust,number_Cluster)
eps=0.5
radius=50
#Label=ApplyDBSCAN(df_3054_Clust,eps,radius)
#Label=Affinity_Propagation(df_3054_Clust)
#Label=Spectral_Clsut(df_3054_Clust,9)
Label=BirchClustering(df_3054_Clust,6) #7 #With Noise(7), Without Noise(6)
display(df_3054_Clust.head())
#Counter
print(Counter(Label))

label=[]
#label=Label
label=shuffleLabelAsPerDescRespRate(df_3054_Clust,Label)
display(df_3054_Clust.head())

Unique_Labels=list((Counter(label)).keys())
print(sorted(Counter(label).items()))

label_df=pd.DataFrame()
label_df=pd.DataFrame.from_dict(Counter(label), orient='index').T
label_df['date']=i_dates

label_df.to_csv(LabelCount, mode='a', index=False, header=False)

#Birch 9: [(0, 499), (1, 952), (2, 1945), (3, 1012), (4, 910), (5, 439), (6, 373), (7, 156), (8, 21)]
#Birch 8: [(0, 499), (1, 1964), (2, 1945), (3, 910), (4, 439), (5, 373), (6, 156), (7, 21)]
#[(0, 548), (1, 212), (2, 574), (3, 578), (4, 112), (5, 730), (6, 708), (7, 801), (8, 491)]
