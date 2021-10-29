import time
import os
import json
import sys

import common_functions as common
from filter_class import Filter

SLEEP_TIME = 1
# PATH = '/dados01/workspace/ufmg.c02dcc/f04_git/mpmg_integracao_f04/configurations.json'

def main():
  
  # if not os.path.isfile(PATH) or not PATH.endswith('.json'):
  #   raise Exception("Não foi possível abrir o arquivo de configuração. Favor checar o caminho e a extensão do arquivo.")
  
  # with open(PATH, 'r') as f:
  #   jason = json.load(f)

  jason = json.loads(sys.argv[1])


  filter_object = Filter(jason)
  read_topics = filter_object.read_topics    

  while True:
    for topic_name, network_name in read_topics.items():      
      try:
          print(common.cyan_string(f'Filtrando mensagens do {network_name}'))
          empty = filter_object.filter_messages(network_name, topic_name, get_key=True, verbose=True)
          
          if not empty:
            print(common.green_string(f'Batch de mensagens da rede {network_name} em {topic_name} foi processada com sucesso.\n'))
          else:
            print(common.magenta_string(f'Tópico {topic_name} do {network_name} não possui novas mensagens.\n'))

      except Exception as e:
        print(f'{e}.\nErro durante o processo de filtragem em {network_name}: {topic_name}. Reiniciando..') 
    
    time.sleep(SLEEP_TIME)

if __name__ == "__main__":
  main()
