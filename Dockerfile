# Use an official Python runtime as a parent image
FROM python:3.11-slim@sha256:ad5dadd957a398226996bc4846e522c39f2a77340b531b28aaab85b2d361210b

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies specified in requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable for FastAPI
ENV PYTHONUNBUFFERED=1

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
