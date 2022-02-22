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
#COPY requirements_clean.txt /
#RUN pip3 install --no-cache-dir -r requirements_clean.txt

COPY requirements.txt /
RUN pip3 install --no-cache-dir -r requirements.txt

#RUN pip3 install tensorflow==2.6.0 --upgrade --force-reinstall

# Install spacy model
#CMD ["python3 -m", "spacy download pt_core_news_sm"]
RUN pip3 install spacy
RUN python3 -m spacy download pt_core_news_sm

# Install nltk stopwords
RUN python3 -m nltk.downloader stopwords

# Create needed folders
RUN mkdir /home/mp && mkdir /home/mp/mounted && mkdir /home/mp/f04 && mkdir /home/mp/f04/utils && mkdir /home/mp/f04/models

# Copy files to specified folders
COPY main.py /home/mp/f04/
COPY common_functions.py /home/mp/f04/
COPY identificacao.py /home/mp/f04/
COPY json_maker.py /home/mp/f04/
COPY metodo_aprendizado_maquina.py /home/mp/f04/
COPY metodo_preliminar.py /home/mp/f04/
COPY utils/helpers.py /home/mp/f04/utils/
COPY utils/political_classification.py /home/mp/f04/utils/
COPY utils/text_processor.py /home/mp/f04/utils/
COPY models/BaseModel.py /home/mp/f04/models/
COPY models/ClassicalModel.py /home/mp/f04/models/
COPY models/CNN.py /home/mp/f04/models/
COPY models/DeepModel.py /home/mp/f04/models/
COPY models/DNN.py /home/mp/f04/models/
COPY models/HAN.py /home/mp/f04/models/
COPY models/LSTMC.py /home/mp/f04/models/
COPY models/NaiveModel.py /home/mp/f04/models/
COPY models/RNN.py /home/mp/f04/models/
COPY models/Transformer.py /home/mp/f04/models/

## TODO Tirar essa linha na producao
COPY configurations.json /home/mp/f04/

# Assure it worked
#RUN pip3 freeze && find /home/mp/ -iname "*py"
RUN pip3 freeze
