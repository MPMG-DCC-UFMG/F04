# -*- coding: utf-8 -*-
import time
import os
import json
import sys

from transcricao_audio import transc
import common_functions as common

SLEEP_TIME = 1

def main():
  
  jason = json.loads(sys.argv[1])

  transc_object = transc(jason)
  read_topics = transc_object.read_topics
  
  while True:
    for topic_name, network_name in read_topics.items():      
      try:
          print(common.cyan_string(f'Filtrando mensagens do {network_name}'))
          empty = transc_object.filter_messages(network_name, topic_name, get_key=True, verbose=True)
          
          if not empty:
            print(common.green_string(f'Batch de mensagens da rede {network_name} em {topic_name} foi processada com sucesso.\n'))
          else:
            print(common.magenta_string(f'Tópico {topic_name} do {network_name} não possui novas mensagens.\n'))

      except Exception as e:
        print(f'{e}.\nErro durante o processo de filtragem em {network_name}: {topic_name}. Reiniciando..')    
    
    time.sleep(SLEEP_TIME)


if __name__ == "__main__":
  main()