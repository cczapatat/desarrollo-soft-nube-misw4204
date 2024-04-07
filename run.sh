#!/bin/bash

docker rm queue_nube postgres_nube worker_nube api_nube

docker rmi desarrollo-soft-nube-misw4204-worker desarrollo-soft-nube-misw4204-api

docker volume rm desarrollo-soft-nube-misw4204_shared-volume

sudo docker-compose -f docker-compose.yaml up