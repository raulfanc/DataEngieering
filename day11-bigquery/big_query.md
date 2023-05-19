in this file, I will play with BG queries to test the performance of the queries

## Create
a table from GCS parquet files

using BG Query to create a table that extracts parquet files [from day 10's work](../day10-prefect_docker)
```sql
CREATE OR REPLACE EXTERNAL TABLE `trips_data_all.external_yellow_tripdata`
OPTIONS (
format = 'Parquet',
uris = ['gs://dtc_data_lake_de-learning-20190409/yellow_tripdata_2021-*.parquet']
);
```

- then the table is created
![](../Pictures/Pasted%20image%2020230519113238.png)

- then we can query the table
```sql
SELECT * FROM `trips_data_all.external_yellow_tripdata` LIMIT 10;
```

![](../Pictures/Pasted%20image%2020230519114349.png)


## Partitioning
- create a non-partitioned table
```sql
CREATE OR REPLACE TABLE `trips_data_all.external_yellow_tripdata_non_partitioned` AS
SELECT * FROM `trips_data_all.external_yellow_tripdata`
```

- create a partitioned table
```sql
CREATE OR REPLACE TABLE `trips_data_all.external_yellow_tripdata_partitioned` 
PARTITION BY 
DATE(pickup_datetime, month) AS
SELECT * FROM `trips_data_all.external_yellow_tripdata`;
```

![](../Pictures/Pasted%20image%2020230519115723.png)

## Comparing
- select vender id from non-partitioned table
```sql
SELECT DISTINCT(VerdorID)
FROM trips_data_all.external_yellow_tripdata_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-01-31';
```

![](../Pictures/Pasted%20image%2020230519120124.png)

- select vender id from partitioned table
```sql
SELECT DISTINCT(VendorID)
FROM trips_data_all.external_yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-01-31';
```
![](../Pictures/Pasted%20image%2020230519120153.png)
**as we can see, the partitioned table take less**


## Look into Partitioning
- check the partitioning in BG Query
```sql
SELECT partition_id, table_name, total_rows
FROM `trips_data_all.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'external_yellow_tripdata_partitioned'
ORDER BY total_rows DESC;
```

![](../Pictures/Pasted%20image%2020230519121720.png)
can use this to inspect bias, as some rows have more data and some rows have less

## Clustering

```sql
-- Creating a partition and cluster table
CREATE OR REPLACE TABLE de-learning-20190409.trips_data_all.yellow_tripdata_partitoned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY PULocationID AS
SELECT * FROM de-learning-20190409.trips_data_all.external_yellow_tripdata;
```
![](../Pictures/Pasted%20image%2020230519122943.png)

**comparing the actual process the data with Partitioning + Clustering**

- query the **partitioning only**
```sql
SELECT count(*) as trips
FROM de-learning-20190409.trips_data_all.external_yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-03-31'
AND PULocationID=1;
```

![](../Pictures/Pasted%20image%2020230519123558.png)

 - query the **partitioning + clustering**
```sql
SELECT count(*) as trips
FROM de-learning-20190409.trips_data_all.yellow_tripdata_partitoned_clustered
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-03-31'
AND PULocationID=1;
```

![](../Pictures/Pasted%20image%2020230519123633.png)