#! /bin/bash

MODELS_FOLDER="/home/mp/mounted/";

# Caso se queira trocar o caminho do arquivo de configuração, altere a variável abaixo:
FILE_PATH="/dados01/workspace/ufmg_2021_f04/model_config/configurations.json"

# Caso se queira trocar o caminho da localização em que se encontram os arquivos dos modelos, modifique a variável abaixo:
X_MODELS_FOLDER="/dados01/workspace/ufmg_2021_f04/model_config/models/"

docker run -v "$X_MODELS_FOLDER:$MODELS_FOLDER" --rm -it -d "$(sudo docker images | grep 'f04_mp' | head -1 | cut -d' ' -f 1)" python3 /home/mp/f04/main.py "$(python3 json_maker.py "$FILE_PATH")" "$X_MODELS_FOLDER" "$MODELS_FOLDER";
