#! /bin/bash

#Organizing volumes at docker container.
AUTH_FOLDER="/var/mp/auth/";
OUTP_FOLDER="/var/mp/output/";
IMG_FOLDER="/var/mp/img/";
#####

##Caso se queira que os caminhos da pasta do autenticador ou do output mudem, deve-se mudar as strings com os endereços abaixo. 
ORIG_AUTH_FOLDER="$PWD/authenticators/";
ORIG_OUTP_FOLDER="$PWD/output/"
#####

##Organizando os arquivos para o container conseguir criar o volume na pasta do arquivo passado.
if [ "$1" == "tsi" ]; then

  if [ -d "$2" ]; then
    echo "ERRO: Foi fornecido um diretório para tsi."
    exit
  fi
  
  FILE_NAME=${2##*/}
  IMG_FOLDER_FINAL=$IMG_FOLDER$FILE_NAME
  X_IMG_FOLDER=${2%"$FILE_NAME"}
  
else

  if [ ! -d "$2" ]; then
    echo "ERRO: Diretório fornecido não existe."
    exit
  fi
  
  X_IMG_FOLDER=$2
  IMG_FOLDER_FINAL=$IMG_FOLDER
fi

docker run -v "$ORIG_AUTH_FOLDER:$AUTH_FOLDER" -v "$ORIG_OUTP_FOLDER:$OUTP_FOLDER" -v "$X_IMG_FOLDER:$IMG_FOLDER" \
 --rm -it "$(docker images | grep 'transcritor_mp' | head -1| cut -d' ' -f 1)" \
 python3 /home/mp/transcricao/main.py "$1" "$AUTH_FOLDER" "$OUTP_FOLDER" "$IMG_FOLDER_FINAL";

