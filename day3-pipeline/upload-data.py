import argparse
import pandas as pd
from sqlalchemy import create_engine
from time import time


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='an integer for the accumulator')
parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

args = parser.parse_args()
print(args.accumulate(args.integers))


engine = create_engine("postgresql://root:root@localhost:5432/ny_taxi")

df_iter = pd.read_csv("../yellow_tripdata_2021-01.csv", iterator=True, chunksize=100000)
df = next(df_iter)

df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)


df = pd.read_csv("../yellow_tripdata_2021-01.csv", nrows=100)

df.head()

pd.io.sql.get_schema(df, name="yellow_taxi_data")



print(pd.io.sql.get_schema(df, name="yellow_taxi_data"))

engine.connect()

print(pd.io.sql.get_schema(df, name="yellow_taxi_data", con=engine))

len(df)

df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

df.head(n=0).to_sql("yellow_taxi_data", con=engine, if_exists="replace")

while True:
    try:
        t_start = time()
        df = next(df_iter)

        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)

        df.to_sql("yellow_taxi_data", con=engine, if_exists="append")

        t_end = time()

        print(f"Chunk loaded in {t_end - t_start} seconds")
    except StopIteration:
        print("All chunks have been loaded.")
        break
