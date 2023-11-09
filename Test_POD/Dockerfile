# Use the official Ubuntu 22.04 image as the base image
FROM ubuntu:22.04

# Set the working directory in the container
WORKDIR /app

# Update package lists and install necessary dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Copy the Python files into the container
COPY test-app.py /app/test-app.py
COPY upbit_defs.py /app/upbit_defs.py

# Install Python dependencies
RUN pip3 install pyupbit boto3 slack_sdk

# Command to run the Python script
CMD ["python3", "test-app.py"]
