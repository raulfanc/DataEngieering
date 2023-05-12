# day10 running flows in Docker

## 1. Scheduling
Once the deployment has been created. we can either 
- going to Prefect UI to schedule the flow
- or we can schedule the flow when building the deployment with cli
schedule is helpful when we want to run the flow periodically

#### going to Prefect UI, and click the `deployed flow` I ran from day9
![](../Pictures/Pasted%20image%2020230512100614.png)
then click `add schedule` will go into detailed schedule section
![](../Pictures/Pasted%20image%2020230512100818.png)
can set different schedules
- intervals
![](../Pictures/Pasted%20image%2020230512101145.png)
- Cron
![](../Pictures/Pasted%20image%2020230512101209.png)
the schedule also can be include in the cli command `-cron <cron expression>` when building the flow
```bash
prefect deployment build <path of the deployment file>:<entry name of the flow> -n <name of the flow in UI> -cron <cron expression>
``` 

---

## 2. running in the docker container
- so far we've done it `locally` as a start point
- can put it on GitHub or any `version control system`, and run it in docker container
- can go with Azure, AWS or GCP to run it in the `cloud`

#### 2.1 build the docker

###### 2.1.1 build [dockerfile](./dockerfile) file
```dockerfile
FROM prefecthq/prefect:2.7.7-python3.9

COPY docker-requirements.txt .

RUN pip install -r docker-requirements.txt --trusted-host pypi.python.org -no-cache-dir

COPY prefect_etl_docker.py opt/prefect/flows/
COPY data opt/prefect/data
```
-   `--trusted-host pypi.python.org`: This flag is used when installing Python packages from the PyPI repository (Python Package Index). It specifies the trusted host for downloading packages. In this case, it sets `pypi.python.org` as the trusted host. This can be useful in certain network configurations where the default PyPI host may not be trusted or accessible.
-   `-no-cache-dir`: This flag is used with `pip install` to disable the cache directory. By default, `pip` caches downloaded packages in a local directory to speed up subsequent installations. Using this flag ensures that the cache is not used, and the packages are installed directly from the source. It can be useful to prevent any conflicts or inconsistencies caused by cached packages during the build process.
**not mandatory to do so, but in real-world application, it is practical in certain scenarios**
- `--trusted-host` flag is often used in enterprise environments or situations where the default **PyPI host** is not accessible or not trusted
- `-no-cache-dir` flag can be useful when you want to ensure that the packages are **installed directly from the source** without any interference from cached files.

###### 2.1.2 build a [docker-requirements.txt](./docker-requirements.txt) file
```docker-requirements.txt
# C+P from the day7's requirements.txt and removed some packages are not needed for today's demo  
  
pandas==1.5.2  
prefect-gcp[cloud_storage]==0.2.4  
protobuf==4.21.11  
pyarrow==10.0.1  
# pandas-gbq==0.18.1  
# psycopg2-binary==2.9.5  
# sqlalchemy==1.4.46  
# prefect==2.7.7  
# prefect-sqlalchemy==0.2.2
```

###### 2.1.3 docker image
1. run bash command to build the `docker image`(cd to where the dockerfile is)
```bash
docker image build -t <name of the docker image>:<tag> .
```
-   `<name of the docker image>`: This is the name you choose for your Docker image. It can be any name you prefer and should be unique to identify your image. For example, you might choose `myapp` as the name of your image.
-   `<tag>`: This is an optional tag that provides a version or identifier for your Docker image. It can help differentiate different versions or variations of the same image. Tags are typically represented as strings, such as `latest`, `v1.0`, `dev`, or any custom value you want. If no tag is specified, the `latest` tag is assumed by default.
2. then login the docker hub with bash
```bash
docker login
```
3. after logged in, go to docker hub website to create a repo if you dont have one..
![](../Pictures/Pasted%20image%2020230512113521.png)
4. tag the image to the docker remote repo with bash
```bash
docker tag <original image name><tag> <docker ID>/<remote repo name>:<repo tag>
```
- `tag` commandline doesn't upload the image, it adds a **new identifier**
- `<docker ID>/<remote repo name> is to link the local original image to a remote docker repo. DO NOT provide the wrong name, this is not a random name.
- `<repo tag>` on the other hand is a version, and it is displaying in the remote repo.

5. then push the image to docker hub
```bash
docker image push <previously defined identifier>
```
- This is the identifier is previsouly defined in the `tag` command.

#### 2.2 configure docker with Prefect UI

###### 2.2.1 go to Prefect UI
- go to `Block` and add `Docker Container` from UI.
- `Image (Optional)` to specify the identifier 
![](../Pictures/Pasted%20image%2020230512122154.png)
- after created the docker container, can use the command below
![](../Pictures/Pasted%20image%2020230512122351.png)
- can include the script below to create and configure the DockerContainer in py script
```python
from prefect.infrastructure.docker import DockerContainer  
  
# alternative way to create DockerContainer block in the UI  
docker_block = DockerContainer(  
image="raulfanc/de-repo:de-day10",  
image_pull_policy="always",  
auto_remove=True,  
)  
  
docker_block.save("prefect-de-docker", overwrite=True)
)
```

###### 2.2.2 deployment with docker
- create a `py script`
```python
from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer   # the DockerContainer class
from prefect_etl_docker import etl_parent_flow              # the flow from the previous snippet

# from the previously configured in UI
docker_container_block = DockerContainer.load("prefect-de-docker")

docker_deploy = Deployment.build_from_flow(
    flow=etl_parent_flow,                   # the entry point flow
    name="prefect-docker-flow",             # the name of the flow showing in deployment UI
    infrastructure=docker_container_block,  # can specify the environment variables here, i.e., AWS, GCP, etc.
)

if __name__ == "__main__":
    docker_deploy.apply()                   # deploy the flow
```

![](../Pictures/Pasted%20image%2020230512124417.png)

- run this script 
```bash
python docker_deploy.py
```
- and start the agent
```bash
prefect agent start  --work-queue "default"
```
- then run the deployment in UI
- have the new files uploaded to GCS
![](../Pictures/Pasted%20image%2020230512141026.png)

#### 2.3 Prefect Profile
refer to [link](https://docs.prefect.io/2.7/concepts/settings/#configuration-profiles)
- using `prefect profile ls` to see what profile we are using
![](../Pictures/Pasted%20image%2020230512124510.png)
- to modify what `specific API endpoint` we need to use [link](https://docs.prefect.io/2.7/concepts/settings/#setting-and-clearing-values)
```bash
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"
```

- then the docker can interact with the `prefect orion server`
![](../Pictures/Pasted%20image%2020230512130218.png)

---

## 3. noted mistakes
- when creating dockerfile to build the docker image, be careful to the COPY line, I had mistake to put 
```dockerfile
COPY prefect_etl_docker.py opt/prefect/flows/  
COPY data opt/prefect/data
```
- which created a nested folder structure in the Prefect docker container
![](../Pictures/Pasted%20image%2020230512140741.png)
- it should be `/opt`, my mistaken one is `opt` which 
```dockerfile
COPY prefect_etl_docker.py /opt/prefect/flows/  
COPY data /opt/prefect/data
```
- this resulted in when running deployment, the prefect doesn't know where to find the script, as Prefect only looking for the path: `opt/prefect/flows` folder.

---

## 4. Q&A

- **Question 1:**  `prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"`, what does it do?
- **Answer 1:** this command is to set the Prefect server running on the local server, if trying to run on a different server, will need to change the ip address

- **Question 2:** the [docker_deployment.py](docker_deploy.py) only uploaded month 1 and 2, why not 3 months?
- **Answer 2:** because in the [prefect_etl_docker.py](prefect_etl_docker.py), I set a default value for `month` to be 2, this time, we are accessing the function from outside, so the `__name__==__main__` is not triggered, so the default value is used.

- **Question 3:** I still fail to visualise Docker, for me docker image is like an `os`, to run programe, so firstly, we need to run the container, like I previously use `pgadmin4` and `postgres 13` container with the `images`. but today, the image can do a lot more?
- **Answer 3:** 
A Docker image is a bit like a lightweight, standalone, and self-sufficient operating system that includes everything needed to run your application: the code, a runtime (like Python), libraries, environment variables, and config files.

When you build a Docker image, you're creating a blueprint or template for running your application. You can think of an **image** as a **class** in object-oriented programming.
   
A Docker **container**, on the other hand, is a running instance of a Docker image. It's like an object in object-oriented programming, which is an **instance** of a class.
   
In your case, your Python script and its dependencies are packaged into a Docker image. When Prefect runs your flow, it creates a Docker container from this image and runs your script inside this container. This is similar to how you ran pgAdmin4 and Postgres in Docker containers. You just don't see the running containers in this case because Prefect manages them for you.

The process is roughly as follows:

1.  Prefect server (running in your local environment or in the cloud) gets a request to run your flow.
2.  Prefect server creates a new Docker container from your image.
3.  Inside this new Docker container, Prefect server runs your flow (which is your Python script).
4.  When the flow finishes running, Prefect server stops and removes the Docker container.

So the Docker container is indeed used, it's just that Prefect manages the lifecycle of the container for you (creating, starting, stopping, and removing the container) so you don't see it directly.

- **Question 4**: Prefect server creates a new Docker container from your image. where is this container? Can i access to it? will it be removed itself when the job is done?
- **Answer 4:** not directly accessible. Prefect manages these containers internally and remove them when the jobs are done.