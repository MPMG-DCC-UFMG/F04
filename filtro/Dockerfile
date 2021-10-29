# Download base image ubuntu 20.04
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

# Create needed folders
RUN mkdir /home/mp && mkdir /home/mp/filtro

COPY src/main.py /home/mp/filtro/ 
COPY src/filter_class.py /home/mp/filtro/ 
COPY src/common_functions.py /home/mp/filtro/

# Assure it worked
RUN pip3 freeze && find /home/mp/filtro -iname "*py"

