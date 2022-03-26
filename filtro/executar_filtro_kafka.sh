#! /bin/bash

# Caso se queira trocar o caminho do arquivo de configuração, altere a variável abaixo:
#FILE_PATH="/datalake/ufmg/f04/configurations.json"
FILE_PATH="/dados01/workspace/ufmg_2021_f04/model_config/configurations.json"

docker run --rm -it -d "$(sudo docker images | grep 'filtro_mp' | head -1 | cut -d' ' -f 1)" \
python3 /home/mp/filtro/main.py "$(python3 json_maker.py "$FILE_PATH")"
