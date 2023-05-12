from prefect.infrastructure.docker import DockerContainer

# alternative way to create DockerContainer block in the UI
docker_block = DockerContainer(
    image="raulfanc/de-repo:de-day10",
    image_pull_policy="always",
    auto_remove=True,
)

docker_block.save("prefect-de-docker", overwrite=True)
