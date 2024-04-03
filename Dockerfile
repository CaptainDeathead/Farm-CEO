# Use a base image compatible with ARM architecture
FROM arm32v7/ubuntu:latest

# Install required packages for cross-compilation and buildozer
RUN apt-get update && \
    apt-get install -y python3-pip build-essential git openjdk-8-jdk unzip && \
    python3 -m pip install --upgrade pip && \
    pip3 install buildozer

# Set the working directory
WORKDIR /app

# Copy your project directory into the container
COPY . /app

# Define environment variables if needed

# Run any necessary commands for building
