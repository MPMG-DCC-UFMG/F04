import os
import json
import io
from google.cloud import vision
from google.auth.exceptions import GoogleAuthError
from google.api_core import exceptions
from datetime import datetime


class Transcriber:
  
  """
  Classe responsável por armazenar os arquivos de autenticação, 
  além de conter os métodos de transcrição de imagens utilizando a biblioteca Google Cloud Vision.

  Métodos
  --------
  transcribe_single_image

  """
  
  def __init__(self, path, verbose=True):
    
    """
    Inicializador

    Parametros
    ----------
    Path: Caminho para a pasta de documentos de autenticação, no formato .json
    
    Verbose: Determina se o programa printará ou não mensagens no terminal.
    
    Retorno
    ---------
    None
    """

    self.__credentials = list()
    self.__credential_num = -1
    self.__path = path
    self.__verbose = verbose
    self.__store_all_credentials(path)
    self.__set_authentication()
    self.__kafka_path = '/var/mp/img/'

    
  def __store_all_credentials(self, path):
    
    """Função entra no caminho passado e armazena todos os jsons de 
    autenticação.
    """

    if not os.path.isdir(path):
      raise Exception("Caminho de autenticadores fornecido não é válido.")
    
    all_jsons = os.listdir(path)
    for item in all_jsons:
      
      if not item.endswith('.json'):
        continue

      self.__credentials.append(item)
  
    if len(self.__credentials) == 0:
      raise Exception('Não foram encontradas chaves de autenticação.')
  
  def __set_authentication(self):
    
    self.__credential_num += 1
    
    if self.__credential_num == len(self.__credentials):
      raise GoogleAuthError("Todas as chaves de autenticações foram usados e/ou não são mais válidas. Favor conferir.")    
    
    full_path = self.__path + self.__credentials[self.__credential_num]
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = full_path

  
  def __read_image(self, image_name):
    """
    Método que realiza a comunicação com a API Cloud Vision do Google e lê uma imagem.
    
    """

    while True:
      try:
        
        client = vision.ImageAnnotatorClient() 

        with io.open(image_name, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations

        final_text = ""
        for text in texts:
          final_text = text.description
          break
        
        return final_text
      
      except (GoogleAuthError, exceptions.PermissionDenied) as e:
        
        print(f'{e}.\nTentando trocar a chave de autenticação.')
        
        self.__set_authentication()
        
      except FileNotFoundError as e:
        
        raise FileNotFoundError('Caminho que contém as imagens não existe ou arquivo de imagem não encontrado.\
          \nFavor verificar o conteúdo do caminho passado após os comandos tsi ou tef.')

      except Exception as e:
        
        raise Exception(f'Erro: {e}. Terminando a execução.')

  def __generate_json(self, text, image_name):
    output = {}
    file_name = (image_name.split('/'))[-1]
    output["nome_do_arquivo"] = file_name
    output["texto_transcrito"] = text
    return json.dumps(output, ensure_ascii=True)

  def __generate_kafka_msg(self, text, image_name):
    output = dict()
    file_name = (image_name.split('/'))[-1]
    output[file_name] = text
    return output

  def transcribe_single_image(self, image_name, kafka=False):
    
    if self.__verbose:
      date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
      file_name = image_name.split('/')
      print(f'[{date}] Início da transcrição: {file_name[-1]}\n')
    
    if kafka == True:
      image_name = self.__kafka_path+image_name

    image_text = self.__read_image(image_name)

    final_j = self.__generate_kafka_msg(image_text, image_name) if kafka == True \
      else self.__generate_json(image_text, image_name)

    return final_j
    


        
    

