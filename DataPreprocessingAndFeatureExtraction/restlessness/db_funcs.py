import pandas as pd
from sqlalchemy import *
import os
#from dotenv import load_dotenv

#load_dotenv()  # take environment variables from .env.

postgres_credentials = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
}
engine = create_engine(
    "postgresql://{user}:{password}@{host}/{db}".format(**postgres_credentials)
)


def get_data(patient_id: str, start_time: str, end_time: str) -> pd.DataFrame:

    sql = f"""
    select tstamp_base, unnest(ts_offset_seconds[:]) as off_sec,
       unnest(data[:][5:5]) as filtered1, 
       unnest(data[:][6:6]) as filtered2,
       unnest(data[:][7:7]) as filtered3,
       unnest(data[:][8:8]) as filtered4 
        from sensor.bed_raw_{patient_id}_only 
        where tstamp_base between '{start_time}'::timestamp and '{end_time}' ::timestamp 
        order by tstamp_base;
    """
    # sql = sql.format(patient_id=patient_id, start_time=start_time, end_time=end_time)

    return pd.read_sql(sql, engine)


def get_data_for_restlessness(
    table_name: str, start_time: str, end_time: str
) -> pd.DataFrame:
    sql = f"""
        SELECT 
            * 
        FROM 
            get_data_for_restlessness('{table_name}', '{start_time}', '{end_time}')
        ORDER BY
            start_tstamp;
    """
    print(f"Getting data for {start_time} to {end_time}")
    result = pd.read_sql(sql, engine)
    print("Done!")
    return result


def format_data_for_restlessness(
    data: pd.DataFrame,
) -> dict:
    """
    Format the data for restlessness.
    """
    result = {
        "r1": data["r1"],
        "r2": data["r2"],
        "r3": data["r3"],
        "r4": data["r4"],
        "start_times": data["tstamp_array"],
    }

    return result


if __name__ == "__main__":
    df = get_data_for_restlessness(
        "bed_raw_3054_only", "2018-08-28 20:31:20.2", "2018-08-28 21:41:20.2"
    )
    first_row = df.iloc[0]

    print(len(first_row["r1"]))
