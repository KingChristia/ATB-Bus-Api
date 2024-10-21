# Use an official Python runtime as a parent image
FROM python:3.13-slim@sha256:751d8bece269ba9e672b3f2226050e7e6fb3f3da3408b5dcb5d415a054fcb061

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
