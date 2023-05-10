## Day 3. Python Script 
#### 1. use day2's code to include into the new pipeline.py, so it can load data in one go.
```terminal
jupyter nbconvert --to script day2-code.ipynb 
```

#### 2. and then change its name to [ingested.py](ingest-data.py)`
```python
import pandas as pd  
from sqlalchemy import create_engine  
from time import time  
import argparse  
import os  
  
  
# Function to process each chunk of data  
def process_chunk(df, engine, table_name, first_chunk=False):  
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)  
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)  
  
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
first_chunk = False # Set the flag to False after the first iteration  
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
```


#### 3. above code used the below
1.  The `argparse` library is used in this script to handle command-line arguments passed to the script. It makes it easier to specify the input parameters (such as database connection details, table name, and CSV file path) when running the script. Using `argparse`, you can define the required arguments and their types, making it easier to parse and validate the input values.

2.  The `if __name__ == "__main__":` statement is used in Python scripts to check whether the script is being run directly as the main program or being imported as a module in another script. When a Python script is run, the `__name__` variable is set to `"__main__"` if the script is the main program. If the script is being imported as a module in another script, the `__name__` variable is set to the script's name. By using this statement, you can control the execution of the script, and in this case, you only want to run the main function if the script is being executed as the main program.

3.  In the original code, the path to the CSV file was provided through the `--url` argument, and the file was downloaded using `wget`. In the modified code I provided in the previous response, the path to the CSV file is provided through the `--url` argument. When running the script, you can provide the absolute path of the CSV file as the value for the `--url` argument, like this: run the below command at the root folder of the project due to csv file path is under the same folder

#### 4. Drop the current table and then

5.  run the url path from **online source**, cd to the root folder of the project as the [ingest.py](ingest-data.py) is located in the `day3-pipeline` folder
```yaml
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

python day3-pipeline/ingest-data.py \
--user root \
--password root \
--host localhost \
--port 5432 \
--db ny_taxi \
--table_name yellow_taxi_data \
--url=${URL}
```

#### 5. using [updated dockerfile](dockerfile) to ingest data
1. in the same folder of day3, create a dockerfile and modify it

2. build a new `docker image` with the [updated dockerfile](dockerfile),
```
docker build -t dockerfile-ingest:v001 .
```

3. start a local server to stimulate 
```
python -m http.server   
```

4. find the ip address so the docker container can access and find the data.

5. list the existing created docker network
```
docker network ls
```

![](../Pictures/Pasted%20image%2020230501143200.png)
(1)  `bridge` - This is the default network created by Docker. Containers launched in this network are isolated from each other and from the host system, but they can communicate with each other and the host through a bridge interface. You shouldn't delete this network  
(2) `host` - This network is for containers that directly use the host's network stack without any isolation. Containers in the host network can access services running on the host and can be accessed from the host directly. It's also a default network, so you shouldn't delete it.
(3) `none` - This is a network with no network interfaces, meaning the containers in this network have no external connectivity. It's useful for creating containers that don't need a network or need a custom network stack. This is also a default network, so you shouldn't delete it.
(4) `pg-network` - This is the custom network you created. Containers in this network can communicate with each other, and it provides isolation from other networks. You can delete this network if you no longer need it, or if you want to recreate it.

6. create a docker network to connect to Docker containers, **already created**
```bash
docker network create pg-network
```

7. then docker run
```bash
URL="http://<ip address>:8000/yellow_tripdata_2021-01.csv"

docker run -it \
--network=pg-network \
dockerfile-ingest:v001 \
--user root \
--password root \
--host postgre-pg-network \
--port 5432 \
--db ny_taxi \
--table_name yellow_taxi_data \
--url=${URL}
```
**note**: the `host` value is associate with the created `postgres` container's `name`