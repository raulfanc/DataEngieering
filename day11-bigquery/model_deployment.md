1. gcloud auth login
2. run terminal
```terminal
bq extract -m de-learning-20190409:trips_data_all.tip_model gs://dtc_data_lake_de-learning-20190409/taxi_ml_model/tip_model
```
3. 
```terminal
mkdir /tmp/model
```
```terminal
gsutil cp -r gs://taxi_ml_model/tip_model /tmp/model
```

```terminal
mkdir -p serving_dir/tip_model/1
```

```bash
cp -r /tmp/model/tip_model/* serving_dir/tip_model/1
```

```bash
docker pull tensorflow/serving
```

```bash
docker run -p 8501:8501 --mount type=bind,source=pwd/serving_dir/tip_model,target= /models/tip_model -e MODEL_NAME=tip_model -t tensorflow/serving &
```

```bash
curl -d '{"instances": [{"passenger_count":1, "trip_distance":12.2, "PULocationID":"193", "DOLocationID":"264", "payment_type":"2","fare_amount":20.4,"tolls_amount":0.0}]}' -X POST http://localhost:8501/v1/models/tip_model:predict
http://localhost:8501/v1/models/tip_model
```