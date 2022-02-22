import os
from posix import listdir
import time
import sys
import json

from module.transcriber import Transcriber
from module.kafka_ocr import Ocr
from google.auth.exceptions import GoogleAuthError

VALID_NUMBER_OF_ARGUMENTS = [5,4]

def tsi(t1, noutput_path, image_name):
  """
  Uma das três opções de execução. TSI significa 'Transcribe single image'.
  Transcreve a imagem e escreve no arquivo .json no caminho indicado.

  Argumentos
  ----------
  t1: Objeto da classe Transcriber
  noutput_path: Caminho final de escrita
  image_name: Caminho e nome da imagem.

  Retorno
  ----------
  None

  """
  
  final_json = t1.transcribe_single_image(image_name)
  write_on_file(final_json, noutput_path)

def tef(t1, noutput_path, target_path):
  """
  Uma das três opções de execução. TEF significa 'Transcribe entire folder'.
  Transcreve todas as imagens e escreve em arquivos .json no caminho indicado.

  Argumentos
  ----------
  t1: Objeto da classe Transcriber
  noutput_path: Caminho final de escrita
  target_path: Caminho das imagens.

  Retorno
  ----------
  None

  """
  sentinel = 0
  image_formats = ['.png', '.jpg', '.jpeg']

  for item in os.listdir(target_path):
    
    if True in [item.endswith(i) for i in image_formats]:
      
      full_path = target_path + item
      
      final_json = t1.transcribe_single_image(full_path)
      
      write_on_file(final_json, noutput_path)
      sentinel +=1

  if sentinel == 0:
    raise Exception('Nenhum arquivo de imagem foi encontrado no caminho passado.')


def create_folder(timestamp, output_path):
  """
  Cria a pasta de saída dentro do caminho indicado e retorna o caminho completo para a escrita.

  Parametros
  ----------
  timestamp: Nome da pasta que será criada, caso ela não exista no diretório
  output_path: Caminho onde a pasta será criada.

  Retorno
  ----------
  full_path: Endereço onde os .jsons serão salvos.

  """

  full_path = output_path + timestamp + '/'
  
  if not os.path.isdir(full_path):
    os.mkdir(full_path)
  
  return full_path 


def write_on_file(jason, new_output_path):
  
  new_timex = str(int(time.time()*1000))
  final_p = new_output_path + new_timex + '.json'

  with open(final_p, 'w') as f:
    f.write(jason) 


def treat_path(path):
  if path[-1] != '/':
    path += '/'
  return path


def main():

  if len(sys.argv) not in VALID_NUMBER_OF_ARGUMENTS:
    raise Exception(f'Número de argumentos passados não é valido. Favor conferir a chamada do programa')
  
  new_complete_path = ""

  command_type = sys.argv[1]
  
  authenticators_path = sys.argv[2]
  
  authenticators_path = treat_path(authenticators_path)

  timestamp = str(int(time.time()*1000))
 
  if command_type == 'tsi' or command_type == 'tef':
    output_path = sys.argv[3]
    output_path = treat_path(output_path)

    if not os.path.isdir(output_path):
      raise Exception("Caminho de saída não é válido.")
  
    try:
      t1 = Transcriber(authenticators_path)
      
      if command_type == 'tsi':
        #Caso a opção seja ler somente um arquivo, a pasta é criada, a imagem é lida e escrita.
        image_name = sys.argv[4]

        if os.path.isdir(image_name):
          raise Exception("Foi fornecido um diretório para o comando tsi.")

        new_complete_path = create_folder(timestamp, output_path)
        tsi(t1, new_complete_path, image_name)

      elif command_type == 'tef':
        
        target_folder_name = sys.argv[4]
        
        if not os.path.isdir(target_folder_name):
          raise Exception("Caminho fornecido que contém as imagens não é válido.")
        
        target_folder_name = treat_path(target_folder_name)
        
        new_complete_path = create_folder(timestamp, output_path)
        tef(t1, new_complete_path, target_folder_name)
          
      else:
        raise Exception(f'Comando de execução fornecido não é valido. \
        \nFavor passar um dos 2 comandos: tsi(transcribe single image) ou tef(transcribe entire folder)')

    except Exception as e:
      
      if os.path.isdir(new_complete_path) and len(listdir(new_complete_path)) == 0:
        os.removedirs(new_complete_path)
      
      raise Exception(f'{e}')


  elif command_type == 'kafka':      
    
    t1 = Transcriber(authenticators_path)
    
    jason = json.loads(sys.argv[3])      
    
    volume_name = sys.argv[4]
    kafka_it = Ocr(jason, volume_name=volume_name)
        
    all_image_topics = kafka_it.read_topics
    while True:  
      try: 
        for topic_name, network in all_image_topics.items():
          
          kafka_it.transcribe_images_in_kafka_messages(topic_name, t1)
      
      except GoogleAuthError as e:
        
        raise GoogleAuthError(f'{e} Falha na autenticação.')
          
      except Exception as e:
        
        print(f"Erro {e}. Reiniciando ferramenta.")
    
  
  print(f'Transcrição de imagem realizada com sucesso. Terminando.')


if __name__ == "__main__":
  main()