# Day 4

#### 1. CSV Dataset 
https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```python
import pandas as pd  
  
df = pd.read_csv('/Users/admin/DataEngineer/DataEngeering/Dataset/taxi_zone_lookup.csv')  

len(df)  
 
pd.io.sql.get_schema(df, name='zone_lookup')  
  
from sqlalchemy import create_engine  
engine = create_engine("postgresql://root:root@localhost:5433/ny_taxi")  
engine.connect()  
 
# create schema and generate names of the columns  
df.head(n=0).to_sql("zone_lookup", con=engine, if_exists='replace')  
 
%time df.to_sql("zone_lookup", con=engine, if_exists='append')
```

#### 2. jupyter notebook to load data
[zoneTable_load.ipynb](zoneTable_load.ipynb) to load the above CSV into the containised Postgres DB
![](../Pictures/Pasted%20image%2020230501184810.png)

#### 3. run SQL quries
1. join 2 tables and make the location ID meaningful
```sql
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
```
2. another way to join 2 tables and make the location ID meaningful
```sql
SELECT  
tpep_pickup_datetime,  
tpep_dropoff_datetime,  
total_amount,  
concat(zpu."Borough", ' / ', zpu."Zone") AS "pickup_location",  
concat(zdo."Borough", ' / ', zdo."Zone") AS "dropoff_location"  
FROM  
yellow_taxi_data t JOIN zone_lookup zpu  
ON t."PULocationID" = zpu."LocationID"  
JOIN zone_lookup zdo  
ON t."DOLocationID" = zdo."LocationID"  
LIMIT 100;
```

3. check whether any trip_locations are not included in the zone table
```sql
SELECT  
tpep_pickup_datetime,  
tpep_dropoff_datetime,  
total_amount,  
"DOLocationID",  
"PULocationID"  
FROM  
yellow_taxi_data t  
WHERE  
-- t."PULocationID" is null  
-- t."DOLocationID" is not null  
"DOLocationID" NOT IN (SELECT "LocationID" FROM zone_lookup)  
LIMIT 100;
```

4. only keep the date with `date_trunc`
```sql
SELECT  
tpep_pickup_datetime,  
tpep_dropoff_datetime,  
date_trunc('DAY', tpep_dropoff_datetime),  
total_amount  
FROM  
yellow_taxi_data t
```

5. only present 'DATE' with `CAST`
```sql
SELECT  
tpep_pickup_datetime,  
tpep_dropoff_datetime,  
CAST(tpep_dropoff_datetime AS DATE),  
total_amount  
FROM  
yellow_taxi_data t
```

6. aggregate to get insights:
```sql
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
```

7 Multi GROUP
```sql
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
```
