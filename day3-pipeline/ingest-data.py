import pandas as pd
from sqlalchemy import create_engine
from time import time
import argparse
import os


# Function to process each chunk of data
def process_chunk(df, engine, table_name, first_chunk=False):
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)

    # If it's the first chunk, create the table and the names of the columns
    if first_chunk:
        df.head(0).to_sql(table_name, con=engine, if_exists="replace")

    df.to_sql(table_name, con=engine, if_exists="append")


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    # the backup files are gzipped, and it's important to keep the correct extension
    # for pandas to be able to open the file
    if url.endswith(".gz"):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    # Set up the engine for connecting to the PostgreSQL database
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    # Read the CSV file in chunks
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    # Set the first_chunk flag to True for the first iteration to create the table and names of the columns
    first_chunk = True

    # Iterate through the chunks and process them
    while True:
        try:
            t_start = time()
            df = next(df_iter)
            process_chunk(df, engine, table_name, first_chunk)
            first_chunk = False  # Set the flag to False after the first iteration
            t_end = time()
            print(f"Chunk loaded in {t_end - t_start} seconds")
        except StopIteration:
            print("All chunks have been loaded.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingesting CSV data to Postgres')

    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    args = parser.parse_args()

    main(args)
