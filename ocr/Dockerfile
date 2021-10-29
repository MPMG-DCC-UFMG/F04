# Download base image ubuntu 16.04
FROM ubuntu:20.04

# Set encoding
ENV LANG C.UTF-8

# Update Ubuntu Software repository
RUN apt-get update -y && apt-get upgrade -y

# Install essential packages
RUN apt-get install -y wget curl zip 

# Install python-related packages and PIP3.
RUN apt-get install python3-pip -y

# Install pip libraries
COPY requirements.txt /
RUN pip3 install --no-cache-dir -r requirements.txt

#Install grpcio
RUN pip3 install grpcio

# Create needed folders
RUN mkdir /home/mp && mkdir /home/mp/transcricao && mkdir /home/mp/transcricao/module

# Creating auth, images and output folders for mounting volumes.
RUN mkdir /var/mp && mkdir /var/mp/output && mkdir /var/mp/auth && mkdir /var/mp/img

# Copy files to specified folders
COPY transcriber/main.py /home/mp/transcricao/
COPY transcriber/module/transcriber.py /home/mp/transcricao/module/
COPY transcriber/module/common_functions.py /home/mp/transcricao/module/
COPY transcriber/module/kafka_ocr.py /home/mp/transcricao/module/

# Assure it worked
RUN pip3 freeze && find /home/mp/ -iname "*py"
