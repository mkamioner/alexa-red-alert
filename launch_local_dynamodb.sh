#! /bin/bash

set -e

container_name="dynamo-db-local-alexa-red-alert"
container_image="amazon/dynamodb-local:2.0.0"
local_port=8042

existing_container_id=$(docker ps --filter name="$container_name" --format "{{.ID}}")

if [ "$existing_container_id" == "" ]; then
  echo "Launching new DynamoDB local container"
  docker run \
    --name $container_name \
    --rm \
    --detach \
    --publish "${local_port}:8000" \
    $container_image \
    -jar DynamoDBLocal.jar -inMemory -sharedDb
else
  echo "Container exists"
fi

sleep 5
