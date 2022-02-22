import os
from posix import listdir
import time
import sys
import json
import requests
import module.common_functions as common
from module.transcriber import TikaTranscriber
from module.kafka_ocr import Ocr

def main():
  jason = json.loads(sys.argv[1])        
  
  authentication_json = json.loads(sys.argv[2])
  
  volume_name = sys.argv[3]
  
  kafka_it = Ocr(jason, volume_name=volume_name)
  
  t1 = TikaTranscriber(authentication_json['bearer-token'])

  all_image_topics = kafka_it.read_topics
  while True:  
    try: 
      for topic_name, network in all_image_topics.items():
        print(common.cyan_string(f'Filtrando mensagens do {network}'))

        kafka_it.transcribe_images_in_kafka_messages(topic_name, t1)
    
    except Exception as e:
      
      raise Exception
  

if __name__ == "__main__":
  main()