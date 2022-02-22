#! /bin/bash

  OUTP_FOLDER="/var/mp/output/";
  IMG_FOLDER="/var/mp/img/";

  AUTH_PATH="$PWD/auth/auth_file.json"
  
  
  # Caso se queira trocar o caminho da localização em que se encontram o arquivo de autenticação, modifique a variável abaixo:  
  #FILE_PATH="/datalake/ufmg/f04/configurations.json"
  FILE_PATH="/dados01/workspace/ufmg_2021_f04/model_config/configurations.json"
  
  # Caso o caminho das mídias se altere, é necessário alterar o parâmetro abaixo:  
  X_IMG_FOLDER="/datalake/ufmg/"

  docker run -v "$X_IMG_FOLDER:$IMG_FOLDER" \
  --rm -it "$(docker images | grep 'ocr_mp' | head -1| cut -d' ' -f 1)" \
  python3 /home/mp/transcricao/main.py "$(python3 json_maker.py "$FILE_PATH")" "$(python3 json_maker.py "$AUTH_PATH")" "$X_IMG_FOLDER";

  docker run -v "/datalake/ufmg:/var/mp/img/" \
  --rm -it "$(docker images | grep 'ocr_mp' | head -1| cut -d' ' -f 1)" \
  python3 /home/mp/transcricao/main.py "$(python3 json_maker.py "$FILE_PATH")" "$(python3 json_maker.py "$AUTH_PATH")" "$X_IMG_FOLDER";

