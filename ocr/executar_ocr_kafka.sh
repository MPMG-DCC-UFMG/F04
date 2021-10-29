#! /bin/bash

  AUTH_FOLDER="/var/mp/auth/";
  OUTP_FOLDER="/var/mp/output/";
  IMG_FOLDER="/var/mp/img/";

  # Caso se queira trocar o caminho da localização em que se encontram o arquivo de autenticação, modifique a variável abaixo:
  ORIG_AUTH_FOLDER="$PWD/authenticators/";
  
  # Caso se queira trocar o caminho do arquivo de configuração, altere a variável abaixo:
  FILE_PATH="/datalake/ufmg/f04/configurations.json"
  
  # Caso o caminho das mídias se altere, é necessário alterar o parâmetro abaixo:  
  X_IMG_FOLDER="/datalake/ufmg/"

  docker run -v "$ORIG_AUTH_FOLDER:$AUTH_FOLDER" -v "$X_IMG_FOLDER:$IMG_FOLDER" \
  --rm -it "$(docker images | grep 'ocr_mp' | head -1| cut -d' ' -f 1)" \
  python3 /home/mp/transcricao/main.py "kafka" "$AUTH_FOLDER" "$(python3 json_maker.py "$FILE_PATH")" "$X_IMG_FOLDER";