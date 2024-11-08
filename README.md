# Semi Suprevised Machine Learning Approach to predict Respiratory Health Decline, unobtrusively using in-home ambient bed sensor.


This is divided into three main steps:<br>
```diff
-Step 1: Data Preprocessing (ETL - cleaning and feature engineering)
-Step 2: Data Mining using BIRCH
-Step 3: Build predictive model (Random Forest) 
```
[Link Text](https://example.com)

## Data Source: Americare aging in place facilities hrdraulic bed sensor data
<img src="[https://example.com/image.png](https://github.com/pallavig702/Predicting-Repiratory-Health-Decline-Leveraging-In-Home-Ambient-Sensing/blob/main/Images/DataSource.png)" alt="Sample Image" width="500">
![test](https://github.com/pallavig702/Predicting-Repiratory-Health-Decline-Leveraging-In-Home-Ambient-Sensing/blob/main/Images/DataSource.png)

<div style="width:300px;">
  <img src="[https://external-image-source.com/image.jpg](https://example.com/image.png](https://github.com/pallavig702/Predicting-Repiratory-Health-Decline-Leveraging-In-Home-Ambient-Sensing/blob/main/Images/DataSource.png)" alt="Description">
</div>


## Step 1: Data Preprocessing (cleaning and feature engineering) of signal data from Hydraulic Bed Sensor Data.<br>
**Step 1: Generate Features**: **Run_FeatureExtractor.py** is the main script to run for feature extraction calling self made packages for ETL.
```diff
-E - EXTRACT
```
  * Extracted data from **POSTGRES DB** - [DataPreprocessingAndFeatureExtraction/GetData.py](https://github.com/pallavig702/Predicting-Repiratory-Health-Decline-Leveraging-In-Home-Ambient-Sensing/blob/main/DataPreprocessingAndFeatureExtraction/GetData.py) 
```diff
-T - TRANSFORM -
```
  * Apply **Butter Worth filter** to extract the signal component with a frequency cutoff of 0.7Hz from a complex signal - [DataPreprocessingAndFeatureExtraction/ApplyFilter.py](https://github.com/pallavig702/Predicting-Repiratory-Health-Decline-Leveraging-In-Home-Ambient-Sensing/blob/main/DataPreprocessingAndFeatureExtraction/ApplyFilter.py) 
  * Apply **Moving Average Curve algorithm** for noise detection - [DataPreprocessingAndFeatureExtraction/MAC_Function3 .py](https://github.com/pallavig702/Predicting-Repiratory-Health-Decline-Leveraging-In-Home-Ambient-Sensing/blob/main/DataPreprocessingAndFeatureExtraction/MAC_Function3%20.py)
  * Find **Peaks** and **valleys** in the waveform signal - [DataPreprocessingAndFeatureExtraction/PeakDetection.py](https://github.com/pallavig702/Predicting-Repiratory-Health-Decline-Leveraging-In-Home-Ambient-Sensing/edit/main/DataPreprocessingAndFeatureExtraction/PeakDetection.py)
```diff
-L - LOAD
```

**Run_FeatureExtractor.py** calls **DataRetrievalCycle.py** to orchestrate data retrieval and signal processing. **DataRetrievalCycle.py** further calls **ExtractFeature.py** and pass the processed signal data to this function which then segments the data into 60 min time windows and extract features and stores the features in files with respective date and time stamps.

![test](https://github.com/pallavig702/Predictive-Modeling---Hydraulic-Bed-Sensor-Data-/blob/main/Images/Data_preprocessing.png)
## Step 2: Building Semi - Supervised ML model
#### * Data Mining of 8-D feature vectors using BIRCH to form a code book.<br>
**Step 2.1: Feature processing**: **Run_DataMergeAndMining.py** to combine the features from multiple dates into one file and process them to refine them with **dimentionality reduction**.<br>
**Step 2.2: Run BIRCH CLustering**: **Run_BIRCH_Clustering.py** <br>
#### * Build predictive model (using code book from previous step) to make future predictions in older adults living in Americare aging-in-place facilities.<br>
![test](https://github.com/pallavig702/Predictive-Modeling---Hydraulic-Bed-Sensor-Data-/blob/main/Images/ModelBuilding.png)
Scripts to Run:
https://europa.dsa.missouri.edu/user/pg3fy/notebooks/IR/COPD/NEW_WORK_For_IE_Ratio_AND_FeatureExtraction_AND_Clustering_PythonPeakDetection/Perform%20Clustering%20Experiments-RuhanFeatures-3054Only-Functionalized-TestFiltering(FINAL%20RIGHT).ipynb
## Step 3: Application - Predictions of respiratory health decline in older adults in Americare aging-in-place facilities by leveraging in-home sensor health monitoring framework.
![test](https://github.com/pallavig702/Predictive-Modeling---Hydraulic-Bed-Sensor-Data-/blob/main/Images/FuturePredictions.png)
Scripts to Run:
