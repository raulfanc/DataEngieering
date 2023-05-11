# using prefect to do etl into Google Cloud Storage
import gzip, logging, requests
from datetime import timedelta
from pathlib import Path
import pandas as pd
from io import BytesIO
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket
from prefect.tasks import task_input_hash


@task(retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def fetch(dataset_url) -> pd.DataFrame:
    """"read csv.gz data from web into pandas"""
    # error handling when fetching data
    try:
        response = requests.get(dataset_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to fetch data") from e

    try:
        content = BytesIO(response.content)
        with gzip.open(content, 'rt') as read_file:
            df = pd.read_csv(read_file)
    except Exception as e:
        raise Exception("Failed to read data") from e

    return df


@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """"clean the data"""
    df['tpep_pickup_datetime'] = pd.to_datetime(df.tpep_pickup_datetime)
    df['tpep_dropoff_datetime'] = pd.to_datetime(df.tpep_dropoff_datetime)
    logging.info(df.head(2))
    logging.info(f"columns: {df.dtypes}")
    logging.info(f"rows: {len(df)}")
    return df


@task()
def write_local(df, colour, dataset_file) -> Path:
    """Write DataFrame out as a locally Parquet file."""
    parquet_path = Path(f"data/{colour}/{dataset_file}.parquet")  # the path to the parquet file
    parquet_path.parent.mkdir(parents=True, exist_ok=True)  # ensure directory exists
    df.to_parquet(parquet_path, compression="gzip")
    return parquet_path


@task()
def write_gcs(parquet_path):
    """Upload this cleaned parquet file to GCS."""
    """need to configure the GCS connection block in the config file."""
    gcs_bucket_block = GcsBucket.load("de-gcs")  # the name of the block in the config file
    gcs_bucket_block.upload_from_path(from_path=parquet_path, to_path=parquet_path.name)
    return parquet_path


@flow()
def etl_web_to_gcs(year: int, month: int, colour: str):
    """"the main etl fucntion"""

    dataset_file = f"{colour}_tripdata_{year}-{month:02}"  # {month:02} means 2 digits
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{colour}/{dataset_file}.csv.gz"

    # etl process
    df = fetch(dataset_url)  # pass dataset_url instead of dataset_file
    df_clean = clean(df)
    parquet_path = write_local(df_clean, colour, dataset_file)
    write_gcs(parquet_path)


"""to call this fn elsewhere without providing these"""
"""arguments, the default values would be used."""
@flow()
def etl_parent_flow(
        months: list =[1, 2],   # default value for months
        year: int = 2021,       # default value for years
        colour: str = "yellow"  # default value for colour
):
    for month in months:
        etl_web_to_gcs(month=month, year=year, colour=colour)


if __name__ == "__main__":
    colour = "yellow"
    months = [1, 2, 3]
    year = 2021
    etl_parent_flow(months, year, colour)
