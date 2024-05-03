#!/bin/bash

docker rm worker_nube api_nube api_image

docker rmi desarrollo-soft-nube-misw4204-worker desarrollo-soft-nube-misw4204-api api_image

docker volume rm desarrollo-soft-nube-misw4204_shared-volume

sudo docker-compose -f docker-compose-base-api.yaml up
sudo docker-compose -f docker-compose.yaml up