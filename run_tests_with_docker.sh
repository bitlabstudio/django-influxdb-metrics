#!/usr/bin/env bash

echo "Building the container..."
docker-compose build

echo "Run the tests..."
docker-compose run --rm app
