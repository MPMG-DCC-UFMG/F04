#! /bin/bash


COMM_OUTPUT_DOCKER="/code/output/community_output/"
CFG_CONT="/code/configuration/"
DATA_CONT='/code/data/'
PKL_CONT='/code/pkl_point/'


#Caso a queira alterar o caminho dos arquivos de configuração, altere a variável 'CFG_PATH' abaixo.
CFG_PATH="$(pwd)/configuration/configuration.json"
###################################################

#Para mudar o caminho que os arquivos intermediários são salvas, altere a variável abaixo.
OUTPUT_ON_FOLDER="$(pwd)/output/community_output/"
######################################################

filename1=$(basename -- "$CFG_PATH")

#Caminho que ele procurará o arquivo de configuração dentro do docker.
FINAL_CFG="/code/configuration/$filename1"

#Caminho para a montagem do volume.
CFG_VOL=$(dirname $(readlink -f "$CFG_PATH"))


DATA_IN=$1
FILE_DIR=$(dirname $(readlink -f "$DATA_IN"))
filename=$(basename -- "$DATA_IN")
FINAL_DATA=$DATA_CONT$filename


DATA_PKL=$2
FILE_PKL_DIR=$(dirname $(readlink -f "$DATA_PKL"))
filename=$(basename -- "$DATA_PKL")
FINAL_DATA_PKL=$PKL_CONT$filename


sudo docker run -v "$CFG_VOL:$CFG_CONT" -v "$OUTPUT_ON_FOLDER:$COMM_OUTPUT_DOCKER" -v "$FILE_DIR:$DATA_CONT" -v "$FILE_PKL_DIR:$PKL_CONT" --rm -it "$(sudo docker images | grep 'f04_backbone' | head -1 | cut -d' ' -f 1)" \
python3 /code/community_characterization/community_characterization.py -cfg $FINAL_CFG -input-file $FINAL_DATA -path_to_save $COMM_OUTPUT_DOCKER -pkl $FINAL_DATA_PKL