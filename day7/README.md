# Day 7 Orchestration with `Prefect`


## Data Lake  

#### 1. why need data lake
**mainly used for big data**
- not all data are structured can be loaded into Data Warehouse
- can store all different data, structured, semi-structured, unstructured
- can be designed as a landing zone
- access data from Data Lake is qucik and easy
- Cheaper storage for big data

#### 2. known problems about data lake
- poor management then into a data swamp
- no versioning
- incompatible schemas for the same data, i.e., the same dataset today been written in Avro, tomorrow been written in Parquet
- No metadata associated, hard for data scientist or downstream consumers to find data
- joins not possible across datasets. lack of FK or PK, and no possibility to join them together
Hence, need to address above issues while using data lake, apply some level of governance to it, i.e., bronze, silver, gold zones and much more.

---

## ETL vs ELT
- ETL for small ammount, typically for Data Warehouse, define data schema and relationship then load, also called **schema on write**
- ELT for big ammount, typically for Data Lake, load data first then define schema and relationship later when need to use them, also called **schema on read**

---

## Workflow Orchestration 

#### 1. basic way to ingest data.

**1. using `anaconda` today to manage venv**
**2. using `prefect` to orchestrate workflow**
**3. using `GCP` to store data**

- check `anaconda` installation
```bash
conda --version
```

![](../Pictures/Pasted%20image%2020230509154640.png)

- list all venv created by `conda`
```bash
conda env list
```

![](../Pictures/Pasted%20image%2020230509155132.png)

- create a conda venv
```bash
conda create -n de-day7 python=3.9
```
`-n` to specify the name of the `conda env`

![](../Pictures/Pasted%20image%2020230509155343.png)

- prepare the `requirements.txt` and install it
```bash
pip install -r requirements.txt
```

- wrongly installed the packages in the wrong venv, use `pip uninstall` to remove them
```bash
pip uninstall -y -r requirements.txt
```
- the secondtime install packages with requirements.txt is faster due to `cache`, remove them to free space.
```bash
rm -rf /Users/admin/Library/Caches/pip
```

- create a `pgadmin4` container to play with today's section
```bash
docker run -it \
-e "PGADMIN_DEFAULT_EMAIL=admin@admin.com" \
-e "PGADMIN_DEFAULT_PASSWORD=test1234" \
-p 5050:80 \
--network pg-network \
--name pg_prefect \
dpage/pgadmin4
```

- create a `postgres` container to play with today's section
```bash
docker run -d \
--name postgres_prefect \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi_postgres_prefect" \
-p 5432:5432 \
--network pg-network \
postgres:13
```

- open pgadmn4 at `http://localhost:5050/` then configure it

![](../Pictures/Pasted%20image%2020230509172850.png)

- run the python script to ingest data into the postgres_prefect container
```bash
python ingest_data.py
```

![](../Pictures/Pasted%20image%2020230509172732.png)

---

##### 2. using Prefect to orchestrate workflow

A **flow** is the most basic Prefect object that is a container for workflow logic and allows you to interact and understand
the state of the workflow. Flows are like functions, they take inputs, preform work, and return an output. We can start
by using the @flow decorator to a main_flow function.

Flows contain **tasks** so let’s transform ingest_data into a task by adding the @task decorator. Tasks are not required for
flows but tasks are special because they receive metadata about upstream dependencies and the state of those
dependencies before the function is run, which gives you the opportunity to have a task wait on the completion of
another task before executing.

- import prefect, the package was pre-installed with the requirements.txt
```python
from prefect import task, Flow
```

- modify the `ingest_data.py` to use prefect
```python
# add @flow decorator to the main_flow function
@flow(name="Ingest data into postgres")
def main_flow():
    pass
```
and 
```python
# add @task decoretor above ingest_data() function
def ingest_data(logprint=True, retry=3):
    pass
```

    on top of those, we have also:
    (1). move the codebloack in the `if __name__ == "__main__" to a main_flow() function
    (2). add `main_flow.run()` to the `if __name__ == "__main__"` block
    (2). take off the `if __name__ == "__main__":` block 
    (3). take off the while loop in the `ingest_data()` function as we already using task() to print the log

- drop the postgres_prefect table and run the `ingest_data_prefect.py` (modified version)
```bash
python ingest_data_prefect.py
```

![](../Pictures/Pasted%20image%2020230510131558.png)

#### 3. breakdown `task` into ETL `tasks` with `Prefect`
 after examing the database, the `passenger_count` colume has some error which doesn't make sense
 ![](../Pictures/Pasted%20image%2020230510132637.png)
Hence, we are going to optimise the ingest_data pipeline. with some `Transformation`, we can remove those invalid data from importing into the database

- import `from prefect.tasks import task_input_hash`
- breakdown the task into **ETL tasks**, refer to the [ingest_data_etl_tasks.py](ingest_data_etl_tasks.py) for more details
- use `prefect orion start` to start the prefect server to see UI
- using Prefect UI to configure the DB credentials ---> `block` section --> `SQLAlchemy Connector`
![](../Pictures/Pasted%20image%2020230510145600.png)

- bash run `python ingest_data_etl_prefect.py` then a new table created (yellow_taxi_trips_cleaned was passed in the script), run query again all invalided data has been excluded

![](../Pictures/Pasted%20image%2020230510145528.png)

- since we broke down the tasks, we can see the `flow` in the prefect UI

![](../Pictures/Pasted%20image%2020230510145847.png)

1. now using Prefect's task system to define each step in your ETL pipeline. This allows Prefect to manage the execution
   of each step, and provides benefits like automatic retries and state management.

2. The `extract_data` task is tagged with "extract" and has a cache key function defined, which enables Prefect to cache
   the result of this task and reuse it in future runs if the input (the URL) hasn't changed. This can significantly
   improve performance if the extraction step is time-consuming or resource-intensive. The cache expiration is set to 1
   day, meaning that if the task is run again with the same input within a day, Prefect will reuse the cached result
   instead of running the task again.

3. The `extract_data` task downloads a file from a URL and reads it into a pandas DataFrame. This DataFrame is then
   returned as the output of the task, and can be used as input to other tasks. This separates the extraction logic from
   the rest of your ETL process, making it easier to maintain and test.

4. The `transform_data` task takes a DataFrame as input, performs some transformations on it (removing rows where the
   passenger count is 0), and returns the transformed DataFrame. This task is separate from the extraction and loading
   tasks, which means you could easily replace or modify the transformation logic without affecting the rest of your ETL
   process.

5. The `load_data` task takes a table name and a DataFrame as input, and loads the DataFrame into a SQL database. Again,
   this task is separate from the extraction and transformation tasks, which makes your ETL process more modular and
   easier to maintain and test. The task also has automatic retries enabled, meaning that if the task fails due to a
   transient error (like a temporary network issue), Prefect will automatically retry it.

6. The `log_subflow` task is a separate flow that can be used to log some information. This flow could be extended to
   perform more complex logging or monitoring tasks.

7. In the `main_flow`, you create a Prefect flow that orchestrates the execution of the tasks. You first
   call `extract_data` with the URL of the file you want to download. The result of this task is then passed
   to `transform_data`, and the result of that task is passed to `load_data`. Prefect automatically manages the
   dependencies between these tasks, ensuring that they are run in the correct order and that the output of one task is
   correctly passed to the next.

So, the main advantages of this new structure are:

- Modularity: Each step in your ETL process is defined as a separate task, which makes your code easier to understand,
  maintain, and test.
- Performance: Prefect can cache the results of tasks and reuse them in future runs, which can significantly improve
  performance.
- Resilience: Prefect automatically retries tasks that fail due to transient errors.
- Orchestration: Prefect manages the dependencies between tasks, ensuring that they are run in the correct order and
  that the output of one task is correctly passed to the next.

The only potential issue is that the `SqlAlchemyConnector` is not imported anywhere in the script. You might need to
import it or define it before using it in the `load_data` task.
