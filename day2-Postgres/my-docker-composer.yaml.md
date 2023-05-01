refer to [apache-airflow/docker-compose.yaml](../Documents/docker-compose_2.3.4.yaml.md)

#### docker container to run postgres
  docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13

#### PostgreSQL container and attach it to the network
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v /Users/admin/DataEngineer/DataEngeering/day2/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network my_network \
  --name pgadmin-postgres \
  postgres:13

  
#### docker container to run pgadmin
  docker run -it \
  -e "PGADMIN_DEFAULT_EMAIL=user@example.com" \
  -e "PGADMIN_DEFAULT_PASSWORD=SuperSecret" \
  -p 5050:80 \
  --network my_network \
  --name pgadmin_container \
  dpage/pgadmin4

#### docker container to create network connect postgres and pgadmin
  docker network create my_network
