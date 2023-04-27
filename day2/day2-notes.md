# batch-loading data into Postgres

Apache has guide to set up docker composer as per below, according to [docker-compose](../Documents/docker-compose_2.3.4.yaml)
```yaml
services:  
postgres:  
image: postgres:13  
environment:  
POSTGRES_USER: airflow  
POSTGRES_PASSWORD: airflow  
POSTGRES_DB: airflow  
volumes:  
- postgres-db-volume:/var/lib/postgresql/data  
healthcheck:  
test: ["CMD", "pg_isready", "-U", "airflow"]  
interval: 5s  
retries: 5  
restart: always
```

we need to customise it to ours as per below and
- -e: is to set up environment variables
- -v: as docker doesn't save data, we need to use **`volumn`** to map the data saved in our local repo
	- `-v` option to use the absolute path to your local folder: `/Users/admin/DataEngineer/DataEngeering/day2/ny_taxi_postgres_data`.
	- updated the path inside the container to be `/var/lib/postgresql/data`, which is the default location where PostgreSQL stores its data in the official `postgres` image.
- -p: map a port from the postgres to the docker container
``` yaml
docker run -it \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v /Users/admin/DataEngineer/DataEngeering/day2/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
postgres:13

```
- `postgres:13` the version of the `posgres` I'd like to run with.

**question 1:** I am not a windows user, can I use `$(pwd)/ny_taxi_postgres_data` instead of the absolute path to my local folder? 
**answer:** can use `$(pwd)/ny_taxi_postgres_data` to represent the absolute path of the `ny_taxi_postgres_data` folder in your current working directory. This is a convenient way.

```yaml
docker run -it \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
postgres:13
```
**question 2:** about the `postgres:13` in the docker command. I just checked installed postgres and my local is postgres 15, not 13. so if I run 13 here, is this relative to my locally installed postgres?
**answer 2**: refers to the version of the PostgreSQL image you want to use for the container. This is independent of any PostgreSQL installations you might have on your local system. if want to run a container with PostgreSQL 15, you can simply replace `postgres:13` with `postgres:15` in the `docker run` command.
**qeustion 3:** I deleted images and containers from the docker desktop GUI as they occupy lots of disk space. however, if I use docker run -it python-pandas, I found this time it is faster than the 1st attempt, I noticed that there is a **`cached`** something? so the `cached` thing is stored somewhere in my local machine I guess? and would they take a lot of storage?
**answer 3**: Docker uses a caching mechanism to speed up the process of building and running containers. When you build or pull an image, Docker stores the image layers in your local machine's Docker cache. Can check how much space is being used by Docker images, containers, and volumes with the following command: `docker system df`, output below:
![](../Pictures/Pasted%20image%2020230428105617.png)
clean up unused images, containers, and volumes to free up disk space `docker system prune`
![](../Pictures/Pasted%20image%2020230428105817.png)
remove all unused images (not just dangling ones), you can add the `-a` flag:
![](../Pictures/Pasted%20image%2020230428105829.png)

#### 1. run the terminal above
![](../Pictures/Pasted%20image%2020230428104931.png)

#### 2. using `pgcli` to access the dockerised database
1. open a new terminal window to `pip install pgcli`
2. run `pgcli --help` to view the help docs to find how: 
![](../Pictures/Pasted%20image%2020230428110342.png)
3. use: `pgcli -h localhost -p 5432 -u root -d ny_taxi` as per `docker-compose`, and working as below: 
![](../Pictures/Pasted%20image%2020230428110843.png)

#### 3. load up data to the postgres with `jupyter notebook`
1. `pip install jupyter and pandas` in local machine, can also use the built docker to do so but more complicated
2. look for ny_taxi data from [CSV dataset](https://github.com/DataTalksClub/nyc-tlc-data) and then use `wget` with the link
3. downloaded the yellow tax trip data in `csv.gz` format then use `gzip` to convert it to `CSV`
![](../Pictures/Pasted%20image%2020230428115200.png)
4. use `head -n 100 yellow_tripdata_2021-01.csv` to see the first 100 rows of the data
5. use ` wc -l yellow_tripdata_2021-01.csv` to count rows
![](../Pictures/Pasted%20image%2020230428115446.png)
6. get to know more information about the dataset, refer to [data dictionary](../Documents/data_dictionary_trip_records_yellow.pdf)
7. `pip install --upgrade ipykernel` otherwise the client cannot render the result of `pd`
8. refer to [code with comments](day2.ipynb) for code.

**question 1:** `sqlalchemy` engined schema has different out to the generic SQL schema, why?
**answer 1:** 
1. a generic SQL schema is not considering any specific database system. This is why you see the data types like `INTEGER`, `REAL`, and `TEXT`.
2.  the `con=engine` argument. This takes into account the spe
3. cific SQL dialect of the database system connected by the engine. In this case, it's PostgreSQL. As a result, you see data types like `BIGINT`, `FLOAT(53)`, and `TIMESTAMP WITHOUT TIME ZONE`.

#### 4. batch-loading
1. column names: head(n=0)
![](../Pictures/Pasted%20image%2020230428130924.png)
2. check whether is successful or not in `pgcli` with `\d yellow_taxi_data;`
![](../Pictures/Pasted%20image%2020230428131219.png)

3. started inserting data
![](../Pictures/Pasted%20image%2020230428131648.png)
4. use iterator to insert data in small chunks
![](../Pictures/Pasted%20image%2020230428132701.png)
5. check again using `pgcli` to ensure all data is inserted, matched the number of records count of the CSV.
![](../Pictures/Pasted%20image%2020230428132902.png)
6. below code is generated by ChatGPT, with a cleaner approach than mine.
```python
import pandas as pd
from sqlalchemy import create_engine
from time import time

# Set up the engine for connecting to the PostgreSQL database
engine = create_engine("postgresql://root:root@localhost:5432/ny_taxi")

# Read the CSV file in chunks
csv_file = "../yellow_tripdata_2021-01.csv"
df_iter = pd.read_csv(csv_file, iterator=True, chunksize=100000)

# Function to process each chunk of data
def process_chunk(df, first_chunk=False):
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    if first_chunk:
        df.head(0).to_sql("yellow_taxi_data", con=engine, if_exists="replace", index=False)
    df.to_sql("yellow_taxi_data", con=engine, if_exists="append", index=False)

# Set the first_chunk flag to True for the first iteration
first_chunk = True

# Iterate through the chunks and process them
while True:
    try:
        t_start = time()
        df = next(df_iter)
        process_chunk(df, first_chunk)
        first_chunk = False  # Set the flag to False after the first iteration
        t_end = time()
        print(f"Chunk loaded in {t_end - t_start} seconds")
    except StopIteration:
        print("All chunks have been loaded.")
        break

```


## Notes:
my postgres container
```
CONTAINER ID   IMAGE         COMMAND                  CREATED       STATUS       PORTS                    NAMES
4f378c0e35a0   postgres:13   "docker-entrypoint.s…"   3 hours ago   Up 3 hours   0.0.0.0:5432->5432/tcp   interesting_ganguly
```

Before taking a break,  should ensure that work is saved and containers are running or stopped properly.

1.  **Save work**: Make sure you saved code in your IDE or text editor. If you have been working on a Jupyter notebook, save the notebook as well.
    
2.  **Check the container status**: Run `docker ps` or `docker container ls` to see the list of running containers. If you want to see all containers (including stopped ones), run `docker ps -a` or `docker container ls -a`.
    
3.  **Stop containers**: If you want to stop the running containers before shutting down your machine, you can use the `docker stop <container_id>` command. Replace `<container_id>` with the container ID or name from the `docker ps` output.
    
4.  **Restart containers**: When you come back and want to continue your work, you can restart your stopped containers with `docker start <container_id>`. Again, replace `<container_id>` with the container ID or name.
    
5.  **Check container logs**: After restarting the containers, you can check their logs to ensure they are running correctly using `docker logs <container_id>`.
