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
