# Semi Suprevised Machine Learning Approach to predict Respiratory Health Decline, unobtrusively using in-home ambient bed sensor.

This is divided into three main steps:<br>
(1) Data Preprocessing (cleaning and feature engineering)<br>
(2) Data Mining using BIRCH<br>
(3) Build predictive model (Random Forest) 

## Data Source: Americare aging in place facilities hrdraulic bed sensor data
![test](https://github.com/pallavig702/Predicting-Repiratory-Health-Decline-Leveraging-In-Home-Ambient-Sensing/blob/main/Images/DataSource.png)

## (1) Data Preprocessing (cleaning and feature engineering) of signal data from Hydraulic Bed Sensor Data.<br>
Scripts to Run: Run_FeatureExtractor.py. Run_FeatureExtractor.py calls DataRetrievalCycle.py to orchestrate data retrieval and signal processing. DataRetrievalCycle.py further calls ExtractFeature.py and pass the processed signal data to this function which then segments the data into 60 min time windows and extract features and stores the features in files with respective date and time stamps.

![test](https://github.com/pallavig702/Predictive-Modeling---Hydraulic-Bed-Sensor-Data-/blob/main/Images/Data_preprocessing.png)
## (2) Building Semi - Supervised ML model
#### * Data Mining of 8-D feature vectors using BIRCH to form a code book.<br>
#### * Build predictive model (using code book from previous step) to make future predictions in older adults living in Americare aging-in-place facilities.<br>
![test](https://github.com/pallavig702/Predictive-Modeling---Hydraulic-Bed-Sensor-Data-/blob/main/Images/ModelBuilding.png)
Scripts to Run:

## (3) Application - Predictions of respiratory health decline in older adults in Americare aging-in-place facilities by leveraging in-home sensor health monitoring framework.
![test](https://github.com/pallavig702/Predictive-Modeling---Hydraulic-Bed-Sensor-Data-/blob/main/Images/FuturePredictions.png)
Scripts to Run:
