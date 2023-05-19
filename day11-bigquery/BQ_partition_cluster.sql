CREATE OR REPLACE EXTERNAL TABLE `trips_data_all.external_yellow_tripdata`
OPTIONS (
format = 'Parquet',
uris = ['gs://dtc_data_lake_de-learning-20190409/yellow_tripdata_2021-*.parquet']
);

SELECT * FROM `trips_data_all.external_yellow_tripdata` LIMIT 10;

CREATE OR REPLACE TABLE `trips_data_all.external_yellow_tripdata_non_partitioned` AS
SELECT * FROM `trips_data_all.external_yellow_tripdata`;

CREATE OR REPLACE TABLE `trips_data_all.external_yellow_tripdata_partitioned`
PARTITION BY
DATE(pickup_datetime, month) AS
SELECT * FROM `trips_data_all.external_yellow_tripdata`;

SELECT DISTINCT(VerdorID)
FROM trips_data_all.external_yellow_tripdata_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-01-31';

SELECT DISTINCT(VendorID)
FROM trips_data_all.external_yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-01-31';

SELECT partition_id, table_name, total_rows
FROM `trips_data_all.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'external_yellow_tripdata_partitioned'
ORDER BY total_rows DESC;

-- Creating a partition and cluster table
CREATE OR REPLACE TABLE de-learning-20190409.trips_data_all.yellow_tripdata_partitoned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY PULocationID AS
SELECT * FROM de-learning-20190409.trips_data_all.external_yellow_tripdata;