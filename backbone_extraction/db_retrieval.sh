#! /bin/bash

DATA_CONT="/code/data/"
CFG_CONT="/code/configuration/"

#Caso a queira alterar o caminho dos arquivos de configuração, altere a variável 'CFG_PATH' abaixo.
CFG_PATH="$(pwd)/configuration/configuration.json"
###################################################

#Para mudar o caminho que os arquivos intermediários são salvas, altere a variável abaixo.
OUTPUT_ON_FOLDER="$(pwd)/data/"
######################################################

filename1=$(basename -- "$CFG_PATH")
FINAL_CFG="/code/configuration/$filename1"
CFG_VOL=$(dirname $(readlink -f "$CFG_PATH"))


sudo docker run -v "$CFG_VOL:$CFG_CONT" -v "$OUTPUT_ON_FOLDER:$DATA_CONT" --rm -it "$(sudo docker images | grep 'f04_backbone' | head -1 | cut -d' ' -f 1)" \
python3 /code/db_retrieval/db_retrieval.py -cfg $FINAL_CFG -pts $DATA_CONT
