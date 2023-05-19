## Internal structure
- data storage in **Colossus**
- compute is in a different section (**Dremel**)
- cheaper solution
- connection needed between storage and compute (**Jupyter** Network)
![](https://lh3.googleusercontent.com/5VpZdY3LQhSyBaHrYdFnQzeawGr1BTZQo8dYhEcYMCa_C8WUpiIb6ze16hm4bKn6Ce1MIjlkRUEs2FEbirTSqNNMAXW7O7IXSlWu4Pt4A6oJlzZwinQZMNNhOzQB1Vu1s8ZT4vtQilidF9SjTjLy5SKF=nw)

BigQuery (BQ) is a Data Warehouse solution offered by Google Cloud Platform.

-   BQ is _**serverless**_. There are no servers to manage or database software to install; this is managed by Google and it's transparent to the customers.
-   BQ is _**scalable**_ and has _**high availability**_. Google takes care of the underlying software and infrastructure.
-   BQ has built-in features like Machine Learning, Geospatial Analysis and Business Intelligence among others.
-   BQ maximizes flexibility by separating data analysis and storage in different _compute engines_, thus allowing the customers to budget accordingly and reduce costs.

Some alternatives to BigQuery from other cloud providers would be AWS Redshift or Azure Synapse Analytics.

![](https://lh6.googleusercontent.com/FNDJ5mZR0dRRQh7CMpP4JYNTHpoutLm31IIwBkn-ZadB97qnkPt8GtIR5vsGrcV9N4DxBpq9bEDNlTnKaVht5omL1nzUJmFCp6FZwEE_kj1E_ovBEKIK2KJ3wL4Il3wGU7FYm5aW-2FCLyWFu0CgAL5e=nw)
BigQuery uses column-oriented: do not query the whole column at one time, queries a few and then doing aggregations

![](https://lh5.googleusercontent.com/vbRgaJutoHr04SgUPwwaO-lwR9p-9VII7E1OR7xggocjMgjMlfbG9Dc6C_mZhbR_oudwABvSHDZbmwof6sNaW_kfps1PaRFbVILIxTojT6263iLGqj_gn5B5X-_G6_dXP5x0Uu16W3xZNnj2z-NGrJMC=nw)

the query as per above, Root Server firstly receives the query
then divide the query further in Mixer (modified query)
Mixer then modify and further divide them into Leaf Node (modified query)
Leaf Node talks to Storage level directly

---

## Pricing

BigQuery pricing is divided in 2 main components: processing and storage. There are also additional charges for other operations such as ingestion or extraction. The cost of storage is fixed and at the time of writing is US$0.02 per GB per month; you may check the current storage pricing [in this link](https://cloud.google.com/bigquery/pricing#storage).

Data processing has a [2-tier pricing model](https://cloud.google.com/bigquery/pricing#analysis_pricing_models):

-   On demand pricing (default): US$5 per TB per month; the first TB of the month is free.
-   Flat rate pricing: based on the number of pre-requested_slots_(virtual CPUs).
    -   A minimum of 100 slots is required for the flat-rate pricing which costs US$2,000 per month.
    -   Queries take up slots. If you're running multiple queries and run out of slots, the additional queries must wait until other queries finish in order to free up the slot. On demand pricing does not have this issue.
    -   The flat-rate pricing only makes sense when processing more than 400TB of data per month.

When running queries on BQ, the top-right corner of the window will display an approximation of the size of the data that will be processed by the query. Once the query has run, the actual amount of processed data will appear in the_Query results_panel in the lower half of the window. This can be useful to quickly calculate the cost of the query.


---
## Big Query
[create a table](big_query.md#Create)

#### BQ Partitioning
![](https://lh3.googleusercontent.com/UaJrhRTcBk1eYT4oGLr1FVmP093G2dv5coVOq_SB4wcI4S50nqvqTKK18RjTpbiWZHxeTpfwMs3d6keZ8ur5ZgxzS2fdgfbMHCxxQoTgxauR2g7Nq05vsO50X51YVcTg1JIHyzl_dXLdDjWCQ5iEkDZX=nw)

[Patitioning](big_query.md#partitioning)
[Look into Partitioning](big_query.md#look-into-partitioning)

#### BQ Clustering

![](https://lh3.googleusercontent.com/NhsYLh6duQH25vd6Fff89LcAFumyaGGoaKFQq5NLyfkRY6OYI8rlplaPjdUY295KuNF83JyfvIH-4Ma9Ewm7Fp9zyAdk8tgCCK5VXzIGLavCDKW61GdpZG1O5vJ05mhJ8_ThPZt2Z3vwH2SHfwZhgwtx=nw)

[Clustering](big_query.md#clustering)
[Comparing Clustering and Partitioning](big_query.md#Comparing)

---


## ML with BigQuery
allows us to create and execute Machine Learning models using standard SQL queries, without additional knowledge of Python nor any other programming languages and without the need to export data into a different system.

The pricing for BigQuery ML is slightly different and more complex than regular BigQuery. Some resources are free of charge up to a specific limit as part of the [Google Cloud Free Tier](https://cloud.google.com/free). You may check the current pricing [in this link](https://cloud.google.com/bigquery-ml/pricing).

BQ ML offers a variety of ML models depending on the use case, as the image below shows:
![](../Pictures/Pasted%20image%2020230519105331.png)

#### Feature Processing https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-auto-preprocessing
- BQ supports both manual and automatic feature processing.
- Carried out some test with ny taxi data in [query](big_query_ml.md)
