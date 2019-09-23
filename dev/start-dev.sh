#!/bin/bash

docker rm -f airflow
#docker rmi airflow
docker rm -f minio
#docker build --no-cache -t airflow -f Dockerfile-dev .

docker run -d --net=host -p 9000:9000 --name minio \
  -e "MINIO_ACCESS_KEY=minio" \
  -e "MINIO_SECRET_KEY=yoyowhiwhi" \
  minio/minio server /data

# -v $(pwd)/data:/data \
docker run -d --net=host -v $(pwd):/opt -w /opt -p 8080:8080 --name airflow airflow
docker exec -it airflow /bin/bash
