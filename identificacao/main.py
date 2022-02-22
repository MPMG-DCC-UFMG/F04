import time
import os, sys
import json

import common_functions as common
from identificacao import IdentificacaoF04

SLEEP_TIME = 1
#PATH = '/dados01/workspace/ufmg.c02dcc/f04_git/mpmg_integracao_f04/configurations.json'


def main():
  # PATH = sys.argv[1]

  # if not os.path.isfile(PATH) or not PATH.endswith('.json'):
  #   raise Exception("Não foi possível abrir o arquivo de configuração. Favor checar o caminho e a extensão do arquivo.")
  
  # with open(PATH, 'r') as f:
  #   jason = json.load(f)

  jason = json.loads(sys.argv[1])

  outside_docker_models_path = sys.argv[2]
  inside_docker_models_path = sys.argv[3]
  
  identificacaof04_object = IdentificacaoF04(jason, outside_docker_models_path, inside_docker_models_path)
  read_topics = identificacaof04_object.read_topics


  while True:
    for topic_id_name, topic_name in read_topics.items():
      try:
          print(common.cyan_string(f'Processando mensagens de {topic_name}'))
          empty = identificacaof04_object.process_messages(topic_name, topic_id_name, get_key=True, verbose=True)

          if not empty:
            print(common.green_string(f'Batch de mensagens da fila {topic_name} em {topic_id_name} foi processada com sucesso.\n'))
          else:
            print(common.magenta_string(f'Tópico {topic_id_name} do {topic_name} não possui novas mensagens.\n'))

      except Exception as e:
        print(f'{e}.\nErro durante o processo de filtragem em {topic_name}: {topic_id_name}. Reiniciando..')

    time.sleep(SLEEP_TIME)


if __name__ == "__main__":
  main()
