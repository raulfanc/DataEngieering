#!/usr/bin/env python
# coding: utf-8
import os
import argparse
from time import time
import pandas as pd

# using SQLAlchemy Connector to connect to postgres with prefect no explosures of credentials
from prefect_sqlalchemy import SqlAlchemyConnector

from prefect import task, flow

# newly added libraries, run it over and over, push the cache result, improve the performance
from prefect.tasks import task_input_hash
# to use timedelta for the cache_expiration, we need to import it
from datetime import timedelta


# take url, download csv, and return pandas dataframe
@task(log_prints=True, tags=["extract"], cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_data(url: str):
    if url.endswith('.csv.gz'):
        csv_name = 'yellow_tripdata_2021-01.csv.gz'
    else:
        csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    return df


# using pandas to clean the data,take off the 0 passenger_count, and return a cleaned data
@task(log_prints=True)
def transform_data(df):
    print(f"pre: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    print(f"post: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    return df


@task(log_prints=True, retries=3)
def load_data(table_name, df):
    # instead of hard-coding credentials, "postgres" is the name of the connection block in the config file
    connection_block = SqlAlchemyConnector.load("postgres")
    # using connection block to connect to postgres
    with connection_block.get_connection(begin=False) as engine:
        # loading up dataframe to postgres
        df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
        # inserting data into postgres
        df.to_sql(name=table_name, con=engine, if_exists='append')


# flow can contain multiple subflows
@flow(name="Subflow", log_prints=True)
def log_subflow(table_name: str):
    print(f"Logging Subflow for: {table_name}")


@flow(name="Ingest data into postgres")
def main_flow(table_name,):
    # user = "root"
    # password = "root"
    # host = "localhost"
    # port = "5432"
    # db = "ny_taxi_postgres_prefect"
    table_name = table_name
    csv_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    # to log the sub_flows
    log_subflow(table_name)
    # extract data phase
    raw_data = extract_data(csv_url)
    # transform data phase
    data = transform_data(raw_data)
    # load data phase
    load_data(table_name, data)


if __name__ == '__main__':
    main_flow(table_name="yellow_taxi_trips_cleaned")
