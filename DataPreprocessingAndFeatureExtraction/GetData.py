
########################################################################################
######### This package mainly was used to extract Sensor data Stored at Postgres Db ####
######### All the processing begins after data is extracted from this package ##########
########################################################################################

## This package script performs pre-processing in signal data
# (i) Gets the Access POSTGRES DB (Cedentials) 
# (ii) Postgres DB Querying for Signal Data Extraction
#########################################################################################################
# INPUT: Feeds on -> Access credentials to get into postgres
# Called as package from script - DataPreprocessingAndFeatureExtraction/DataRetrievalCycle.py
# OUTPUT: Yields -> Signal Data pulled from postgres db
#########################################################################################################

import os
import random
import datetime
import numpy as np
import pandas as pd
from sqlalchemy import *
import matplotlib.pyplot as plt
# Imported for signal filtering
from scipy.signal import butter, filtfilt


########################################################################################
###################### Access POSTGRES DB (Cedentials) #################################
########################################################################################
postgres_credentials = {
    'user': 'ecowner',
    'password': 'Jamal.s',
    'db': 'eldercare_dev'
}

engine = create_engine('postgresql://{user}:{password}@ecr.rnet.missouri.edu/{db}'.format(**postgres_credentials))
metadata_obj = MetaData(schema='sensor')
table_3054 = Table("bed_raw_3054_only",
                 metadata_obj,
                Column("es_id"),
                Column("tstamp_base"),
                Column("ts_offset_seconds"),
                Column("data"))
conn = engine.connect()


########################################################################################
###################### Postgres DB Querying Format Function ############################
########################################################################################
def get_Raw_data(Start,End,Res_ID,engine2,table):
    #table='sensor.bed_raw_3083_only'
    #table also carries the ID of the resident whose data is to be extracted
    fmt='%Y-%m-%d %H:%M:%S.%f'
    #var='3083'
    query_params = {'Table' : table, 'Start': Start, 'End': End}
    parse_dates_var={'Start':fmt,'End':fmt}

    sql_select_statement = "select tstamp_base, unnest(ts_offset_seconds[:]) as off_sec,\
        unnest(data[:][1:1]) as raw1,\
       unnest(data[:][2:2]) as raw2,\
       unnest(data[:][3:3]) as raw3,\
       unnest(data[:][4:4]) as raw4,\
       unnest(data[:][5:5]) as filtered1,\
       unnest(data[:][6:6]) as filtered2,\
       unnest(data[:][7:7]) as filtered3,\
       unnest(data[:][8:8]) as filtered4 from "+table+" \
    where tstamp_base between %(Start)s AND %(End)s"
    result=pd.read_sql_query(sql_select_statement,engine2, params=query_params,parse_dates=parse_dates_var)
    result['TimeStamp'] = pd.to_datetime(result['tstamp_base']) + pd.to_timedelta(result['off_sec'], unit='s')
    result=result.drop(columns=['tstamp_base','off_sec'])

    return(result)


