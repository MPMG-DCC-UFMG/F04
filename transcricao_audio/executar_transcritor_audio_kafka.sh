#! /bin/bash

  DATA_FOLDER="/data";
  
  # Caso se queira trocar o caminho do arquivo de configuração, altere a variável abaixo:
  #FILE_PATH="/datalake/ufmg/f04/configurations.json"
  FILE_PATH="/dados01/workspace/ufmg_2021_f04/model_config/configurations.json"
  
  # Caso o caminho das mídias se altere, é necessário alterar o parâmetro abaixo:  
  X_DATA_FOLDER="/datalake/ufmg/telegram"

  docker run -v "$X_DATA_FOLDER:$DATA_FOLDER"\
  --rm -it -d "$(docker images | grep 'transcricao_audio_mp_v1' | head -1| cut -d' ' -f 1)" \
  python3 /app/main.py "$(python3 json_maker.py "$FILE_PATH")";
