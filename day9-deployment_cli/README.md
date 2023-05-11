# day9. Parameterization and Prefect Deployment

## 1. Parameterization

1. refer to the new script [etl_to_gcs_para.py](parameterized_flow.py) C+P from [day8-scripts](../day8-prefect_to_gcs/etl_to_gcs.py)
2. moved some of global variables (parameters) into `(arguments)` of the `parent_flow`
   - allowing flow to take parameters, pass parameters to runtime. multiple flows can be created from a single flow definition
   - create a `parent_flow` and pass parameters to the `child_flow` (the original flow)
3. add `hash_key_fn` to the fetch (extract) task to cache the data as we always do
4. delete the parquet data in gcs from day8, and run the python script.
![](../Pictures/Pasted%20image%2020230511203729.png)

![](../Pictures/Pasted%20image%2020230511203812.png)

![](../Pictures/Pasted%20image%2020230511204639.png)
this was defined within the parent flow and passed parameters in the `__name__=="__main__"`
```python
for month in months:  
etl_web_to_gcs(month=month, year=year, colour=colour)
# ===========================
if __name__ == "__main__":
months = [1, 2, 3]
```

---
## 2. Deployment with Prefect

![](../Pictures/Pasted%20image%2020230511204425.png)
A deployment in Prefect is a server-side concept that encapsulates a flow, allowing it to be scheduled and triggered via the API.

A flow can have multiple deployments and you can think of it as the container of metadata needed for the flow to be scheduled. This might be what type of infrastructure the flow will run on, or where the flow code is stored, maybe it’s scheduled or has certain parameters.

There are two ways to create a deployment. One is using the CLI command and the other is with python.

### 2.1 [CLI](https://docs.prefect.io/latest/concepts/deployments/#create-a-deployment-on-the-cli)

##### 2.1.1 `deployment build` command
`deployment build` command is used to create a deployment from a flow.
```bash
prefect deployment build \
parameterized_flow.py:etl_parent_flow \
-n "para_n_gcp"
```
- `parameterized_flow.py:etl_parent_flow` is the **path to the flow** and the **entry point to the flow**
- `-n` is the name of the deployment you can see in the UI (optional)

##### 2.1.2 a `yaml` file is created
[etl_parent_flow.yaml](etl_parent_flow.yaml)
- parameter is not passed yet, can modify from there
- pass the parameters into the `yaml` file, in **dictionary format** as below
```yaml
parameters: {"colour": "yellow", "months": [1, 2, 3], "year": 2021}
```
also can be edited here on the UI
![](../Pictures/Pasted%20image%2020230512001141.png)
![](../Pictures/Pasted%20image%2020230512001228.png)

##### 2.1.3 `deployment create` command
when the yaml file is configured, by running below command, the deployment is applied
```bash
prefect deployment apply etl_parent_flow-deployment.yaml
```

##### 2.1.4 click `quick run` in the UI to run the flow, and then 
the previous step won't run the flow yet, because there is no **Agent** picked up the job, so:
![](../Pictures/Pasted%20image%2020230512001705.png)
![](../Pictures/Pasted%20image%2020230512001947.png)
##### 2.1.4 prefect agent 
A prefect Agent is needed to run the flow, to start an agent, run below command:
```bash
prefect agent start  --work-queue "default"
```

- now we have the agent running the prefect job

![](../Pictures/Pasted%20image%2020230512002058.png)

- and go back to UI, we can see the job is running

![](../Pictures/Pasted%20image%2020230512002142.png)

##### 2.1.5 set up Notification

![](../Pictures/Pasted%20image%2020230512002510.png)

---

## 3. Q&A 

1.  **Why do we need this `parent_flow`?**
    The parent flow adds flexibility to your ETL process by allowing you to iterate over a range of parameters. This could be useful in situations where you need to process data for different combinations of parameters, for example, for different months, years, or types of taxi trips (identified by "colour" here). Instead of running the child ETL flow manually for each parameter set, you can now simply run the parent flow, which will take care of managing these multiple executions for you.

2.  **Is it an improvement? From where specifically?**

    Yes, it is an improvement in terms of code modularity, readability, and automation.
    -   _Modularity_: By separating the ETL process into child and parent flows, the code is easier to maintain and debug. The child flow is focused on the core ETL logic for a single set of parameters, while the parent flow manages the iteration over different parameter sets.
    -   _Readability_: It's easier for other developers to understand the purpose of each flow and how they interact with each other. The parent flow clearly shows that the ETL process is intended to be run for different combinations of parameters.
    -   _Automation_: The parent flow automates the process of running the ETL flow for different parameters. This reduces the manual effort and possibility of errors involved in running these flows individually.

3.  **Parameterization still has some global variables included, what does it do here?**
    The purpose of parameterization in Prefect is to make your flows more flexible and reusable. In your script, the `etl_parent_flow` function takes the months, year, and colour as parameters, allowing you to run the ETL process for any combination of these values.

    The global variables at the bottom of the script (in the `if __name__ == "__main__"` block) seem to be used for defining the default parameters when you run the script directly. These values are passed to the `etl_parent_flow` function, which then runs the ETL process for each month specified in the `months` list.

    It's worth noting that having these global variables isn't strictly necessary for the parameterization to work. They are just being used here to define default values for running the script. You could also run the `etl_parent_flow` function directly with any other parameters you want, without relying on these global variables.

---

## 4.  use cases to use orchestration tools like airflow/prefect

**Term 1: Conditional execution**

Consider a scenario where you're processing data from an API, and you want to perform different transformations based on whether the data meets a certain condition. For example, if the data represents weather information, you might want to process it differently based on whether the temperature is above or below a certain threshold.
```python
from prefect import Flow, task, case
from prefect.tasks.control_flow import ifelse


@task
def get_weather_data():
    # Fetch the weather data from an API (returning a dictionary for this example)
    return {"temperature": 75, "humidity": 60}


@task
def process_hot_weather(data):
    # Process the data for hot weather
    return f"Hot weather: {data}"


@task
def process_cold_weather(data):
    # Process the data for cold weather
    return f"Cold weather: {data}"


@task
def is_hot_weather(data):
    return data["temperature"] > 70


with Flow("weather-data") as flow:
    weather_data = get_weather_data()
    is_hot = is_hot_weather(weather_data)
    
    with case(is_hot, True):
        hot_weather_result = process_hot_weather(weather_data)
    
    with case(is_hot, False):
        cold_weather_result = process_cold_weather(weather_data)

flow.run()

```

In this example, the `case` statement is used along with the `is_hot` variable to determine which processing function to call. This is a simple example of conditional execution.


**Term 2: Parallelization**

Imagine you're running a social media analysis platform, and you want to fetch data from multiple social media platforms simultaneously. Since fetching data from each platform is independent of the others, you can parallelize these tasks.
```python
from prefect import Flow, task
from prefect.executors import DaskExecutor
import time


@task
def fetch_twitter_data():
    time.sleep(2)  # Simulate a time-consuming API call
    return "Twitter data"


@task
def fetch_facebook_data():
    time.sleep(2)  # Simulate a time-consuming API call
    return "Facebook data"


@task
def fetch_instagram_data():
    time.sleep(2)  # Simulate a time-consuming API call
    return "Instagram data"


@task
def process_data(data):
    return f"Processed {data}"


with Flow("social-media-data") as flow:
    twitter_data = fetch_twitter_data()
    facebook_data = fetch_facebook_data()
    instagram_data = fetch_instagram_data()
    
    processed_twitter_data = process_data(twitter_data)
    processed_facebook_data = process_data(facebook_data)
    processed_instagram_data = process_data(instagram_data)

executor = DaskExecutor()
flow.run(executor=executor)
```
In this example, we have three tasks fetching data from Twitter, Facebook, and Instagram, respectively. Since these tasks are independent, Prefect can run them in parallel using the `DaskExecutor`. This allows the tasks to be executed concurrently, reducing the total execution time.

**Term 3: Dependency management**
dependencies are defined by passing the output of one task as an argument to another task. This clearly defines the order in which tasks should be executed. In your code, you have demonstrated this: the `fetch` task's output is passed to `clean`, `clean`'s output is passed to `write_local`, and `write_local`'s output is passed to `write_gcs`. This forms a chain of dependencies where each task depends on the output of the previous one.
refer to [parameterized_flows.py](parameterized_flow.py)