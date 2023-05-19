### 1. exam the data set
- A few columns such as PULocationID are categorical in nature but are represented with integer numbers in the original table. We cast them as strings in order to get BQ to automatically preprocess them as categorical features that will be one-hot encoded.
- Our target feature for the model will be `fare_amount`. We drop all records where `fare_amount` equals zero in order to improve training.
```sql
-- CREATE A ML TABLE WITH APPROPRIATE TYPE
CREATE OR REPLACE TABLE `de-learning-20190409.trips_data_all.yellow_tripdata_ml` (
`passenger_count` INTEGER,
`trip_distance` FLOAT64,
`PULocationID` STRING,
`DOLocationID` STRING,
`payment_type` STRING,
`fare_amount` FLOAT64,
`tolls_amount` FLOAT64,
`tip_amount` FLOAT64
) AS (
SELECT CAST(passenger_count AS INT64), trip_distance, cast(PULocationID AS STRING), CAST(DOLocationID AS STRING),
CAST(payment_type AS STRING), fare_amount, tolls_amount, tip_amount
FROM `de-learning-20190409.trips_data_all.external_yellow_tripdata_partitioned` WHERE fare_amount != 0
);
```
Using cast to change the data types we desire to use.

### 2. build a model with Linear Regression
```SQL
CREATE OR REPLACE MODEL `de-learning-20190409.trips_data_all.tip_model`
OPTIONS
(model_type='linear_reg',
input_label_cols=['tip_amount'],
DATA_SPLIT_METHOD='AUTO_SPLIT') AS
SELECT
*
FROM
`de-learning-20190409.trips_data_all.yellow_tripdata_ml`
WHERE
tip_amount IS NOT NULL;
```
- `model_type='linear_reg'` specifies the model type as linear regression.
- `input_label_cols=['tip_amount']` specifies the column to be predicted, which is the targeted value, has to be a numerical value.
- `DATA_SPLIT_METHOD='AUTO_SPLIT'` specifies the split method, which is auto split.
- `WHERE tip_amount IS NOT NULL` specifies the condition that the targeted value cannot be null.
- `SELECT *` specifies all the columns to be used in the model.
- `FROM yellow_tripdata_ml` specifies the table to be used in the model.
- `CREATE OR REPLACE MODEL tip_model` specifies the name of the model, and replace the model if it already exists.

### 3. Check features
```sql
SELECT * FROM ML.FEATURE_INFO(MODEL `de-learning-20190409.trips_data_all.tip_model`);
```
`ML.FEATURE_INFO` function returns the information about the features used in the model.
![](../Pictures/Pasted%20image%2020230519143355.png)

### 4. Evaluate the model
```sql
SELECT
*
FROM
ML.EVALUATE(MODEL `de-learning-20190409.trips_data_all.tip_model`,
(
SELECT
*
FROM
`de-learning-20190409.trips_data_all.yellow_tripdata_ml`
WHERE
tip_amount IS NOT NULL
));
```
![](../Pictures/Pasted%20image%2020230519143626.png)

### 5. Predict the model
```sql
SELECT
*
FROM
ML.PREDICT(MODEL `de-learning-20190409.trips_data_all.tip_model`,
(
SELECT
*
FROM
`de-learning-20190409.trips_data_all.yellow_tripdata_ml`
WHERE
tip_amount IS NOT NULL
));
```
![](../Pictures/Pasted%20image%2020230519143950.png)

### 6. Top 3 features
```sql
-- PREDICT AND EXPLAIN
SELECT
*
FROM
ML.EXPLAIN_PREDICT(MODEL `de-learning-20190409.trips_data_all.tip_model`,
(
SELECT
*
FROM
`de-learning-20190409.trips_data_all.yellow_tripdata_ml`
WHERE
tip_amount IS NOT NULL
), STRUCT(3 as top_k_features));
```
STRUCT(3 as top_k_features) in the ML.EXPLAIN_PREDICT() function is an optional argument used to specify the number of top contributing features you want to include in the explanation output. Here, you are requesting that BigQuery includes the top 3 features that contribute the most to each prediction.

In other words, for each row in your prediction results, BigQuery ML will return additional columns indicating which 3 features were the most influential in making that specific prediction.

This can be really useful in real-world applications for understanding and interpreting your model's predictions. For instance, if you have a model predicting housing prices, the ML.EXPLAIN_PREDICT() function could tell you that for a specific prediction, the top contributing features were the number of bedrooms, the house's age, and its proximity to the city center. This kind of information can be invaluable for understanding how your model is working, and for interpreting its predictions in a meaningful way.

Remember, you should choose top_k_features based on your specific use-case. If you want to understand the impact of more features on the model's decision, you can increase this number.

Also note that the ML.EXPLAIN_PREDICT() function is used mainly for debugging and understanding your model better. It's not usually included in the production prediction pipeline unless there's a specific requirement for model interpretability.![](../Pictures/Pasted%20image%2020230519144326.png)

### 7. Hyperparameter tuning

refer to [this link](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create-glm) to see more tuning methods.
```sql
-- HYPER PARAM TUNNING
CREATE OR REPLACE MODEL `de-learning-20190409.trips_data_all.tip_hyperparam_model`
OPTIONS
(model_type='linear_reg',
input_label_cols=['tip_amount'],
DATA_SPLIT_METHOD='AUTO_SPLIT',
num_trials=5,
max_parallel_trials=2,
l1_reg=hparam_range(0, 20),
l2_reg=hparam_candidates([0, 0.1, 1, 10])) AS
SELECT
*
FROM
`de-learning-20190409.trips_data_all.yellow_tripdata_ml`
WHERE
tip_amount IS NOT NULL;
```

This SQL query is used to perform hyperparameter tuning on a linear regression model using BigQuery ML. The goal is to find the optimal values for the hyperparameters of the model to improve its performance. Let's break it down line by line:

-   `CREATE OR REPLACE MODEL`: This statement creates a new model or replaces an existing model. In this case, a new model named `tip_hyperparam_model` will be created in the `trips_data_all` dataset of the `de-learning-20190409` project.
    
-   `OPTIONS (model_type='linear_reg', input_label_cols=['tip_amount'], DATA_SPLIT_METHOD='AUTO_SPLIT', num_trials=5, max_parallel_trials=2, l1_reg=hparam_range(0, 20), l2_reg=hparam_candidates([0, 0.1, 1, 10]))`: Here, we are specifying the options for model training.
    
    -   `model_type='linear_reg'`: This indicates that a linear regression model is being trained.
    -   `input_label_cols=['tip_amount']`: This specifies that 'tip_amount' is the target variable (i.e., the variable we are trying to predict).
    -   `DATA_SPLIT_METHOD='AUTO_SPLIT'`: This option lets BigQuery handle the splitting of data into training and validation sets automatically.
    -   `num_trials=5`: This specifies that the hyperparameter tuning process will try 5 different combinations of hyperparameters.
    -   `max_parallel_trials=2`: This means that two trials will be run in parallel.
    -   `l1_reg=hparam_range(0, 20)`: This specifies that the L1 regularization parameter (which can help prevent overfitting by penalizing large coefficients in the model) should be tuned over a range from 0 to 20.
    -   `l2_reg=hparam_candidates([0, 0.1, 1, 10])`: This specifies that the L2 regularization parameter (which also helps prevent overfitting by penalizing large coefficients in the model) should be tuned over the specified set of values: 0, 0.1, 1, and 10.
-   `AS SELECT * FROM` de-learning-20190409.trips_data_all.yellow_tripdata_ml `WHERE tip_amount IS NOT NULL;`: Finally, this part of the query specifies the data to be used for training the model. The model will be trained on all columns from the `yellow_tripdata_ml` table where the 'tip_amount' column is not null.
    

In a real-world scenario, you would use this type of query when you want to optimize the performance of your linear regression model by tuning its hyperparameters. By specifying different ranges or sets of values for hyperparameters, you can find the combination that results in the best performance of your model on the validation set. This can ultimately lead to more accurate predictions when the model is applied to new, unseen data.

![](../Pictures/Pasted%20image%2020230519145536.png)

### 8. Export the model to GCS datalake
refer to [model_deployment](model_deployment.md) for step by step guide.

```bash
bq extract -m de-learning-20190409:trips_data_all.tip_model gs://dtc_data_lake_de-learning-20190409/taxi_ml_model/tip_model
bq extract -m de-learning-20190409:trips_data_all.tip_hyperparam_model gs://dtc_data_lake_de-learning-20190409/taxi_ml_model/tip_hyperparam_model
```

![](../Pictures/Pasted%20image%2020230519150919.png)
