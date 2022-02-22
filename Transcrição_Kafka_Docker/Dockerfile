# Download base image ubuntu 16.04
FROM ubuntu:16.04


# Set encoding
ENV LANG C.UTF-8

# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# COPY requirements to /app dir
COPY requirements.txt /app

# Install any needed packages specified in base.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# COPY the source code
COPY source /app

# Set the default run command
CMD python main.py


# Update Ubuntu Software repository
#RUN apt-get update -y && apt-get upgrade -y

# Install essential packages
#RUN apt-get install -y wget curl zip

# Install kafka-needed java library and zookeeper
#RUN apt-get install  default-jre -y
#RUN apt-get install oracle-java8-installer -y
#RUN apt-get install zookeeperd -y

# Install ffmpeg
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Create needed folders
#RUN mkdir /data && mkdir /data/kafka

# Install kafka-scripts
# COPY data/kafka.tgz /home/mp/Downloads/kafka/kafka.tgz
#RUN wget https://downloads.apache.org/kafka/2.6.0/kafka_2.13-2.6.0.tgz -O /data/kafka/kafka.tgz
#RUN tar -xvzf /data/kafka/kafka.tgz --strip 1 --directory /data/kafka/