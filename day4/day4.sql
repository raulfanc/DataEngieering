 SELECT
     tpep_pickup_datetime,
     tpep_dropoff_datetime,
     total_amount,
     concat(zpu."Borough", ' / ', zpu."Zone") AS "pickup_location",
     concat(zdo."Borough", ' / ', zdo."Zone") AS "dropoff_location",
 FROM
     yellow_taxi_data t JOIN zone_lookup zpu
         ON t."PULocationID" = zpu."LocationID"
     JOIN zone_lookup zdo
         ON t."DOLocationID" = zdo."LocationID"
 LIMIT 100;



 SELECT
 tpep_pickup_datetime,
 tpep_dropoff_datetime,
 total_amount,
 concat(zpu."Borough", ' / ', zpu."Zone") AS "pickup_location",
 concat(zdo."Borough", ' / ', zdo."Zone") AS "dropoff_location"
 FROM
 yellow_taxi_data t,
 zone_lookup zpu,
 zone_lookup zdo
 WHERE
 t."PULocationID" = zpu."LocationID" AND
 t."DOLocationID" = zdo."LocationID"
 LIMIT 100;

 SELECT
     tpep_pickup_datetime,
     tpep_dropoff_datetime,
     total_amount,
     "DOLocationID",
     "PULocationID"
 FROM
     yellow_taxi_data t
 WHERE
 --     t."PULocationID" is null
 --     t."DOLocationID" is not null
     "DOLocationID" NOT IN (SELECT "LocationID" FROM zone_lookup)
 LIMIT 100;

 SELECT
     tpep_pickup_datetime,
     tpep_dropoff_datetime,
     date_trunc('DAY', tpep_dropoff_datetime),
     total_amount
 FROM
     yellow_taxi_data t;


 SELECT
     tpep_pickup_datetime,
     tpep_dropoff_datetime,
     CAST(tpep_dropoff_datetime AS DATE),
     total_amount
 FROM
     yellow_taxi_data t;


 SELECT
     CAST(tpep_dropoff_datetime AS DATE) as "day",
     count(1) AS "count",
     MAX(total_amount),
     MAX(passenger_count)
 FROM
     yellow_taxi_data t
 GROUP BY
     CAST(tpep_dropoff_datetime AS DATE)
 -- ORDER BY "day" ASC;
 ORDER BY "count" DESC;


SELECT
    CAST(tpep_dropoff_datetime AS DATE) as "day",
    "DOLocationID",
    count(1) AS "count",
    MAX(total_amount),
    MAX(passenger_count)
FROM
    yellow_taxi_data t
GROUP BY
    1, 2
ORDER BY
    "day",
    "DOLocationID";


