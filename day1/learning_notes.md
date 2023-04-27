### Docker + Postgres

#### 1. why do we need docker?
Docker provides container solutions, means we can create multiple containised systems to host different services. 
- Isolation: packs an application's dependencies, so that it can run consistently in any envs, to reduce the conflicts that different services needed running on the same system
- Portability: can be built and run on any system that supports Docker.
- Scalability: it allows horizontally scale up, increase/decrease the number of instances on demand.
- Version Control: Docker Images can be versioned, this enables your application can run in different versions, roll back to previous versions if neccessary.
- Saving resources: comparing to VMs, containers share the [host system's kernel](https://en.wikipedia.org/wiki/Kernel_(operating_system)) so that they use less resources.

#### 2. Creating a simple "data pipeline" in Docker
a simple data pipeline can run different containers which can be assigned to different tasks, lets say the data pipeline has 3 stages, E, T, and L, with Docker, each stage can have its own [dockerfile]. For example, we could create:
-   `Dockerfile-extraction`: Install tools and libraries required for data extraction (e.g., web scraping, connecting to APIs, or databases).
-   `Dockerfile-transformation`: Install tools and libraries required for data transformation (e.g., data processing or cleaning libraries).
-   `Dockerfile-loading`: Install tools and libraries required for data loading (e.g., connecting to a data warehouse or another storage solution).

#### 3. run docker
- need to have `docker daemon` running, which is the docker client, [download](https://www.docker.com/)
- type in terminal
```terminal
docker run hello-world
```
if successful, below message will be displayed in terminal
![[Pasted image 20230427215442.png]]
- when in a container, type `exit` to exit the current container

#### 4. docker images
```terminal 
(venv) (base) admin@REXY DataEngeering % docker run -it ubuntu bash root@33617103bab3:/# ls bin boot dev etc home lib media mnt opt proc root run sbin srv sys tmp usr var 
``` 
when I run a docker container, I noticed there are many files created along with this, where are those files stored locally in my macbook? can I permernently delete them?
- When you run a Docker container, it is created from a Docker image, which is essentially a snapshot of a filesystem
- should not manually delete or modify files inside the Docker data directory. If you want to delete images or containers, you should use the Docker command-line interface or `Docker Desktop GUI`. 
- run `docker images` to list all images, then `docker rmi -f <image_id>` 
![[Pasted image 20230427221242.png]]

#### 5. common mistake with docker images and container
I did the followings:
- `docker run -it python:3.9` to run a python images, to exit it, use 'Ctrl+D'
- `docker run -it --entrypoint=bash python:3.9` to override the entrypoint, from there, type `python` to go into python shell, used `pip install pandas` and then type `python` to go to the python shell, finally type `import pandas` , it is working
- then, I used `docker run -it --entrypoint=bash python:3.9` again the `pandas` lib is not installed, why?
**Answer:** 1st time to use `entrypoint` created a container which is seperate to the base image container (docker run -it python:3.9). after exit, if run the same command, it doesn't go back to the **quitted contained**, instead, it create another container. so the `pandas` lib is not working for this newly created container.

**Solution 1**: use `docker ps -a` to find the container where the `pandas` is installed, as per the screenshot below, there are 3 containers running:
![[Pasted image 20230427224259.png]]
and access with the container_id can bring us back to the container where `pandas` is installed, bash: `docker start CONTAINER_ID`

**Solution 2**: use `dockerfile` , this is more practical, To persist changes, such as installing the `pandas` library, you have a couple of options:
1.  Create a custom Docker image with the required libraries pre-installed. To do this, create a new `Dockerfile` with the following content:
```dockerfile
FROM python:3.9  
  
RUN pip install pandas  
  
ENTRYPOINT [ "bash" ]
```
2. Build the custom image using the `docker build` command: bash: `docker build -t python-pandas . 
3. Now, cd to the directory where the `dockerfile` is, then run: bash:`docker run -it --entrypoint=bash python-pandas`, a container using the custom image (from `docker file`), and it will have the `pandas` library pre-installed.
![[Pasted image 20230427230243.png]]
4. with testing and learning, I've created so many `containers` below
![[Pasted image 20230427231700.png]]
including those that are currently running and those that have exited. 
5. if some containers are not useful and only wanted to keep the useful containers, can use ```
```
docker ps -a --format '{{.ID}}\t{{.Image}}' | grep -v 'python-pandas1'
```
- Lists all containers (`docker ps -a`).
-  Formats the output to show only the container ID and image name, separated by a tab (`--format '{{.ID}}\t{{.Image}}'`).
-  Filters the output using `grep -v`, which inverts the search and shows lines that do not contain the specified pattern (`'python-pandas1'`).
The output will display the container IDs and image names for all containers not based on the `python-pandas1` image.
![[Pasted image 20230427232454.png]]
- then use bash: `docker rm CONTAINER_ID_1 CONTAINER_ID_2 CONTAINER_ID_3`
![[Pasted image 20230427232646.png]]

#### 6. include a python script in the `dockerfile`
modify the `dockerfile`
![[Pasted image 20230427233357.png]]
work pwd is now at `/app`
![[Pasted image 20230427233536.png]]

#### 7. output date and modified `endpoint`
![[Pasted image 20230427234323.png]]

![[Pasted image 20230427234308.png]]

