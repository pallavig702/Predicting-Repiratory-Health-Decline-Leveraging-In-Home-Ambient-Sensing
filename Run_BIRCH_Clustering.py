###########################################################################################
# This script is part of Step 2: Data Mining/Clustering of 8-D feature vectors (as mentioned in Readme).
# (i)imports the necessary features,
# (ii) creates a dendrogram for visualization of hierarchy in data, and
# (iii) uses BIRCH clustering to group the data.
# (iv) The clustered data is further visualized in a 2D projection space using t-SNE plots.
###########################################################################################


import time
import os, sys
import pandas as pd
import numpy as np
import matplotlib
#from matplotlib import pyplot
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as shc

# Packages related to BIRCH
from numpy import where
from numpy import unique
from sklearn.cluster import Birch
from sklearn.datasets import make_classification
from sklearn.datasets.samples_generator import make_blobs
plt.rcParams.update({'font.size': 22})

# Packages related to TSNE Projections
import matplotlib
import seaborn as sns
from sklearn.manifold import TSNE


############################################################################################
############### import the features extracted fron Run_DataMergeAndMining.py script ########
############################################################################################

df_Comb=pd.read_csv('ExtractedFeatureFile.csv')

############################################################################################
########################### Dendogram for Heirarchical Clustering ##########################
####### Dendrogram building helps in identifying the num_clusters hyperparameters 
################### for hierarchial clustering algorithms
############################################################################################

# To extract for specific ID
i_dates='3054'#'3083'#
df_3054_1=df_Comb[df_Comb['ID']==i_dates]


IDdd=df_3054_1['ID'].to_list()
Index=df_3054_1['Index'].to_list()
dates=df_3054_1['Date'].to_list()
print(np.unique(dates))
df_3054_Clust=df_3054_1.drop(columns=['ID','Date','Index'])
df_3054_Clust.head()

pyplot.figure(figsize=(10, 7))  
pyplot.title("Dendrograms")  
matplotlib.rcParams.update({'font.size': 22})

#This generates a dendrogram visualization
dend = shc.dendrogram(shc.linkage(df_3054_Clust, method='ward'))


###########################################################################################
############################# BIRCH Clustering Function ###################################
###########################################################################################

# define dataset

def BirchClustering(X,n):
    model = Birch(threshold=0.01, n_clusters=n)
   
    # fit the model
    model.fit(X)
    # assign a cluster to each example
    yhat = model.predict(X)
    # retrieve unique clusters
    clusters = unique(yhat)
    # create scatter plot for samples from each cluster
    X, clusters = make_blobs(n_samples=X.shape[0], centers=len(clusters), cluster_std=0.70, random_state=0)
    plt.scatter(X[:,0], X[:,1], alpha=0.7, edgecolors='b')
    plt.scatter(X[:,0], X[:,1], c=clusters, cmap='rainbow', alpha=0.7)#, edgecolors='b')
    return(yhat)



df_3054_1=df_Comb[df_Comb['ID']==i_dates]
IDdd=df_3054_1['ID'].to_list()
Index=df_3054_1['Index'].to_list()
dates=df_3054_1['Date'].to_list()
print(np.unique(dates))
df_3054_Clust=df_3054_1.drop(columns=['ID','Date','Index'])
display(df_3054_Clust.head())

Clustered_data=BirchClustering(df_3054_Clust,6) #7 #With Noise(7), Without Noise(6) # This number 6 got by building dendrogram of data.
display(df_3054_Clust.head())

#Counter
print(Counter(Label))

Clustered_data_renamed_label=shuffleLabelAsPerDescRespRate(df_3054_Clust,Clustered_data) #For visualization purpose labels were renamed.
display(df_3054_Clust.head())

Unique_Labels=list((Counter(Clustered_data_renamed_label)).keys())
print(sorted(Counter(Clustered_data_renamed_label).items()))

labelled_df=pd.DataFrame()
labelled_df=pd.DataFrame.from_dict(Counter(Clustered_data_renamed_label), orient='index').T
labelled_df['date']=i_dates

labelled_df.to_csv(LabelCount, mode='a', index=False, header=False)



#################################################################################################
##### BUILD 2-D TSNE PROJECTIONS OF HIGH DIMENSIONAL DATA colored by cluster category ###########
#################################################################################################

####################### Functions for building TSNE #######################
def CallTNSE2(data, Label,titleName,date,path,alpha):#,Res_ID):
    #Source: https://www.datatechnotes.com/2020/11/tsne-visualization-example-in-python.html
    #Source: https://seaborn.pydata.org/generated/seaborn.scatterplot.html
    #STEP 1: TRANSFORM DATA
    data=data.drop(columns=['label'])
    display(data.head())
    tsne = TSNE(n_components=2, verbose=1, random_state=123,perplexity=120)#,early_exaggeration=40.0) #perplexity=50,
    z = tsne.fit_transform(data)
    
    #perplexity=100 this worked,#early_exaggeration=40.0
    display(z)
    #STEP 2: PROJECT MULTIDIMENSIONAL DATA IN 2D
    df = pd.DataFrame()
    df["y"] = Label
    #df["id"]=Res_ID
    df["comp-1"] = z[:,0]
    df["comp-2"] = z[:,1]
    
    matplotlib.rcParams.update({'font.size': 16})

    c=Counter(Label)
    num_clust=len(c.keys())
    #color_dict = dict({'COPD':'brown','Non-COPD':'green'})
    sns_plot = sns.scatterplot(x="comp-1", y="comp-2", hue=df.y.tolist(),
                    palette=sns.color_palette("hls", num_clust),\
                    data=df,alpha=alpha)
    #palette=color_dict

    #ADD NUMBERS TO PLOT
    for label in df.y.unique():
    # randomly sample
        tmp = df.loc[df['y']==label].sample(1)
        #add label to some random points per group
        for _,row in tmp.iterrows():
            plt.annotate(label, (row['comp-1'], row['comp-2']), size=14, weight='bold', color='k')
     
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    #sns_plot.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
    #sns.move_legend(sns_plot, "upper left", bbox_to_anchor=(1, 1))
    plt.savefig(path+"/"+date+"_"+titleName+".png") 
    return()

####################### Call For BULDING TSNE #######################
alpha=1
CallTNSE2(df_3054_Clust, labelled_df, "Clustered data",i_dates,Resultpath,alpha)
#CallTNSE2(df_3054_Clust, label, "Clustered data",i_dates,Resultpath,alpha)
