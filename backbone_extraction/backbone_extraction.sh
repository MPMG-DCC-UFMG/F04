#! /bin/bash

DATA_CONT="/code/data/"
BACKBONE_CONT="/code/output/backbone_files/"
CFG_CONT="/code/configuration/"

DATA_IN=$1

#Caso a queira alterar o caminho dos arquivos de configuração, altere a variável 'CFG_PATH' abaixo.
CFG_PATH="$(pwd)/configuration/configuration.json"
###################################################

#Para mudar o caminho que os arquivos intermediários são salvas, altere a variável abaixo.
OUTPUT_ON_FOLDER="$(pwd)/output/backbone_files/"
######################################################

filename1=$(basename -- "$CFG_PATH")
FINAL_CFG="/code/configuration/$filename1"
CFG_VOL=$(dirname $(readlink -f "$CFG_PATH"))

FILE_DIR=$(dirname $(readlink -f "$DATA_IN"))
filename=$(basename -- "$DATA_IN")

FINAL_DATA=$DATA_CONT$filename

sudo docker run -v "$CFG_VOL:$CFG_CONT" -v "$OUTPUT_ON_FOLDER:$BACKBONE_CONT" -v "$FILE_DIR:$DATA_CONT" --rm -it "$(sudo docker images | grep 'f04_backbone' | head -1 | cut -d' ' -f 1)" \
python3 /code/backbone_extraction/backbone_extraction.py -pfx MPMG -cfg $FINAL_CFG -inf $FINAL_DATA
