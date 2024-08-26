# Use an official Python runtime as a parent image
FROM python:3.12-slim@sha256:59c7332a4a24373861c4a5f0eec2c92b87e3efeb8ddef011744ef9a751b1d11c

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
