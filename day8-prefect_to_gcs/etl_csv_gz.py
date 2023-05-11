# using prefect to do etl into Google Cloud Storage
import gzip
from pathlib import Path
import pandas as pd
import requests
from io import BytesIO
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket


@task(retries=3)
def fetch(dataset_url) -> pd.DataFrame:
    """"read csv.gz data from web into pandas"""

    # we set retries=3, and manually create a failure to test the retry mechanism
    # from random import randint
    # if randint(0, 1) > 0:
    #     raise Exception("Randomly failed to fetch the data")
    response = requests.get(dataset_url, verify=False)
    content = BytesIO(response.content)
    with gzip.open(content, 'rt') as read_file:
        df = pd.read_csv(read_file)

    return df


@task(log_prints=True)
def clean(df=pd.DataFrame) -> pd.DataFrame:
    """"clean the data"""
    df['tpep_pickup_datetime'] = pd.to_datetime(df.tpep_pickup_datetime)
    df['tpep_dropoff_datetime'] = pd.to_datetime(df.tpep_dropoff_datetime)
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    return df


@flow()
def etl_web_to_gcs():
    """"the main etl fucntion"""
    colour = "yellow"
    year = 2021
    month = 1
    dataset_file = f"{colour}_tripdata_{year}-{month:02}"  # {month:02} means 2 digits
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{colour}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)  # pass dataset_url instead of dataset_file
    df_clean = clean(df)
    path = write_local(df_clean, dataset_file)


if __name__ == "__main__":
    etl_web_to_gcs()
