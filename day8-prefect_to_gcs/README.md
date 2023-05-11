
- run postgre13 and pgadmin4 with docker-compose refer to [docker-compose.yaml](docker-compose.yml)
```bash
docker-compose up -d
```

![](../Pictures/Pasted%20image%2020230511110247.png)

- prefect to read csv.gz data from url and clean it, refer to [etl_csv_gz.py](etl_csv_gz.py)
![](../Pictures/Pasted%20image%2020230511120106.png)

- on top of that, we have an improved [etl_to_gcs.py](etl_to_gcs.py) to ingest data into GCS, saved in Parquet format

- configure the Prefect's block section to add GCP's credentials.
```bash
prefect block register -m prefect_gcp
```

![](../Pictures/Pasted%20image%2020230511120911.png)

- add `GCS Bucket` from `Blocks` on Prefect UI

#### for [etl_to_gcs.py](etl_to_gcs.py), I've done:

1. Error Handling: While the fetch task has a retry mechanism, it would be good to add some error handling within the
   task itself. If the requests.get call fails, or if the downloaded file is not in the expected format, should
   handle these exceptions and raise meaningful errors.
2. moving global variables to at the top of the script to improve readability
3. replaced `print func` with `proper logging`, which can provide more flexibility and control over the output.
4. `parquet_path.parent.mkdir(parents=True, exist_ok=True)` to ensure directory exists

---

#### with the improved script, Ive succesfully 
**1. written a cleaned parquet file to specific local folder**
**2.  and then automatically uploaded to GCS bucket**

![](../Pictures/Pasted%20image%2020230511171600.png)

--- 

#### Warning:
![](../Pictures/Pasted%20image%2020230511170307.png)
indicating that **pandas** has encountered **a column with mixed types**, which could potentially lead to incorrect data handling. In pandas, a single dataframe column can only store one datatype. If different types of data are stored in the same column, pandas will try to infer the most appropriate datatype, but sometimes it might make incorrect assumptions which leads to warnings like this.

#### Solution:
the column with index 6 (7th column if we start counting from 1) has mixed types. To resolve this warning:
- specify the correct datatype for this column when reading the CSV file
- or, if the column is not needed, drop it from the dataframe
- or, if **not sure**, can specify 'str' or 'object' to handle any type of data

can modify the pd.read_csv() call to explicitly specify the datatype for the 7th column:
```python
df = pd.read_csv(read_file, dtype={6: 'str'})
```
This line will read the CSV file into a DataFrame, but it will treat the 7th column as strings regardless of what type
of data it actually contains.

when dealing with multiple columns, can use below example:
```python
df = pd.read_csv(read_file, dtype={6: 'str', 7: 'int'})
```
**The column indices in the dtype dictionary are 0-based, so the first column is 0, the second is 1, and so on.**