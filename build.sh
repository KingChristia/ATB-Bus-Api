#!/bin/bash

# Define variables
IMAGE_NAME="fastapi-atb"
CONTAINER_NAME="6ab6f47e121e"
DOCKERFILE_PATH="." # Path to your Dockerfile, typically the current directory

# Step 1: Pull the latest changes from the repository (if applicable)
echo "Pulling latest changes from the repository..."
git pull origin main

# Step 2: Stop and remove the existing container
echo "Stopping and removing the existing container..."
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

# Step 3: Remove the old Docker image
echo "Removing the old Docker image..."
docker rmi $IMAGE_NAME

# Step 4: Build the new Docker image
echo "Building the new Docker image..."
docker build -t $IMAGE_NAME $DOCKERFILE_PATH

# Step 5: Run the new container
echo "Running the new container..."
docker run -d --name $CONTAINER_NAME -p 8000:80 $IMAGE_NAME

# Step 6: Clean up dangling images (optional)
echo "Cleaning up dangling Docker images..."
docker image prune -f

echo "Docker update completed successfully!"
