#! /bin/bash

MODELS_FOLDER="/home/mp/mounted/";

# Caso se queira trocar o caminho do arquivo de configuração, altere a variável abaixo:
FILE_PATH="/datalake/ufmg/f04/configurations.json"

# Caso se queira trocar o caminho da localização em que se encontram os arquivos dos modelos, modifique a variável abaixo:
X_MODELS_FOLDER="/datalake/ufmg/f04/"

docker run -v "$X_MODELS_FOLDER:$MODELS_FOLDER" --rm -it "$(sudo docker images | grep 'f04_mp' | head -1 | cut -d' ' -f 1)" python3 /home/mp/f04/main.py "$(python3 json_maker.py "$FILE_PATH")" "$X_MODELS_FOLDER" "$MODELS_FOLDER";