from logging import exception
from typing import final

from .common_functions import KafkaInteractor
from .common_functions import * 
from google.auth.exceptions import GoogleAuthError

import json
import copy

FIELDS = ['imagens']
OCR_VERSION = 'Google Cloud Vision [Google OCR]'


STT = "STT"
NERR = "NERR"
ERR = "ERR"


class Ocr(KafkaInteractor):
  
  def __init__(self, configuration_file, volume_name=None):
    
    super().__init__(configuration_file)

    self.__valid_consumers = self._KafkaInteractor__get_valid_consumers(FIELDS)
  
    self.__volume_name = volume_name if volume_name != None else 'ufmg/'

  def transcribe_images_in_kafka_messages(self, topic_name, obj, verbose=False):
    
    
    message_batch = None
    
    consumer = None

    try:
      timeout_batch = int(self._KafkaInteractor__timeouts['timeout_batch'])*1000
      
      consumer = self._KafkaInteractor__connect_kafka_consumer(topic_name, batch_num=3)
      #Não é garantido o retorno de mensagens em um primeiro poll. Por isso 2 ou mais chamadas consecutivas é uma boa ideia.
      
      for _ in range(2):
        message_batch = consumer.poll(timeout_batch)
        if len(message_batch) != 0:
          break
      
      error = None
      
      new_message = ""
      
      empty = True

      for topic_partition, partition_batch in message_batch.items():
          for message in partition_batch:
              final_message = (message.key.decode('utf-8'), message.value.decode('utf-8'))
              
              error, new_message, empty_message = self.__transcribe_image(final_message[1], obj)
              
              if error == ERR:
                raise Exception(f'{message} Erro durante o processo de transcrição. Parando ferramenta de OCR.')
        
              elif error == STT:
                new_message['motivo_erro'] = "Arquivo não encontrado." 
                if publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['error_topic_name'], json.dumps(new_message), final_message[0], get_key=True):
                  if verbose : print(green_string('Transcrição de mensagem feita com sucesso.'))            
              
              elif error == NERR:
                if new_message:
                  
                  if not publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['text_topic_name'], json.dumps(new_message), final_message[0], get_key=True):
                    if verbose : print(green_string('Transcrição de mensagem feita com sucesso.'))
                
                
                if empty_message:
                  self.__send_to_trash(json.dumps(empty_message), final_message[0], get_key=True, verbose=True)


              empty = False
              
              consumer.commit({topic_partition: OffsetAndMetadata(message.offset+1, "no metadata")})

      consumer.close()
      
      return empty
    
    
    except GoogleAuthError as e:
      
      error_msg = {}
      error_msg['erro'] = e
      self.__send_to_error(json.dumps(error_msg), final_message[0], get_key=True)
      raise GoogleAuthError(f'{e} Falha na autenticação.')

    except Exception as e:
      
      try:
        
        consumer.commit({topic_partition: OffsetAndMetadata(message.offset+1, "no metadata")})
        
        consumer.close()
        
        motive = f"Erro: {e}"
        
        destined_message = json.loads(copy.deepcopy(final_message[1]))
        
        destined_message['erro'] = motive
        
        self.__send_to_error(json.dumps(destined_message), final_message[0], get_key=True)
      
      except:
        pass
      
      raise Exception(f'{e} Erro na ferramenta.')

  def __transcribe_image(self, message, obj):
    
    transcribe_list = list()
    empty_list = list()
    
    new_message = ""
    
    full_message = ""
    
    empty_message = ""

    try:
      
      new_message = json.loads(copy.deepcopy(message))

      new_message['versao_ferramenta'] = OCR_VERSION

      if "midias" in new_message:

        image_msg = new_message['midias']

        for item in image_msg:
          
          full_path = item['caminho']
                  
          image_path = full_path.split(self.__volume_name)[1]
          
          text = obj.transcribe_single_image(image_path, kafka=True)
          
          transcribe_list.append(text) if any([True for key,value in text.items() if len(value) != 0]) else \
            empty_list.append(text)
      
      elif "datalake" in new_message:
        image_msg = new_message["datalake"]
        
        image_path = image_msg.split(self.__volume_name)[1]

        text = obj.transcribe_single_image(image_path, kafka=True)
        
        transcribe_list.append(text) if any([True for key,value in text.items() if len(value) != 0]) else \
          empty_list.append(text)

      if len(empty_list) > 0:
        
        empty_message = copy.deepcopy(new_message)
        
        empty_message['motivo_descarte'] = f"Imagens transcritas nao possuem texto."
        
        empty_message['texto'] = empty_list

      
      if len(transcribe_list) > 0:
        
        full_message = copy.deepcopy(new_message)
        
        full_message['texto'] = transcribe_list


      return NERR, full_message, empty_message
    
    except (FileExistsError, FileNotFoundError):
      return STT, new_message, None

    except GoogleAuthError as e:
      raise GoogleAuthError(f'{e}. Falha na autenticação.')

    except Exception as e:
      return ERR, e, None
    
 
 
  def __send_to_trash(self, message, key, get_key=False, verbose=False):
      """
      Método que realiza o envio para o tópico de descarte. Isso ocorre se a mensagem estiver no período fornecido no arquivo
      de entrada (ou seja, estiver dentro do período eleitoral).
      
      
      """
      date = datetime.now()
      if not publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['discard_topic_name'], message,key, get_key):
          if verbose: print(red_string(f"[{date}] Envio da mensagem para o tópico falhou."))
          raise Exception('Mensagem não pode ser enviada para o tópico de descarte.')

 
 
  def __send_to_error(self, message, key, get_key=False, verbose=False):
      date = datetime.now()
      if not publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['error_topic_name'], message,key, get_key):
          if verbose: print(red_string(f"[{date}] Envio da mensagem com para o tópico de lixo falhou."))
          raise Exception('Mensagem não pode ser enviada para o tópico de erro.')
          




if __name__ == '__main__':
  pass


