# -*- coding: utf-8 -*-
import speech_recognition as sr
import os
import json
import copy
from datetime import datetime

from common_functions import KafkaInteractor
import common_functions as common

ALLOWED_NETWORKS = ['audio']

class transc(KafkaInteractor):
    
    def __init__(self, configuration_file):

        super().__init__(configuration_file)

        self._KafkaInteractor__get_valid_consumers(ALLOWED_NETWORKS)

        self.__texto = configuration_file["texto"] if "texto" in configuration_file else True
        
        self.__imagem = configuration_file["imagem"] if "imagem" in configuration_file else True
        
        self.__audio = configuration_file["audio"] if "audio" in configuration_file else True

        self.__datas = configuration_file["datas"] if "datas" in configuration_file else []
    
    
    def filter_messages(self, network_name, topic_name, get_key=False, verbose=False):
        """
        Método checa se existem mensagens na fila relacionadas ao topico de audio
        
        """
        empty = True
        
        try:
            consumer = self._KafkaInteractor__connect_kafka_consumer(topic_name)
            
            for _ in range(5):
                message_batch = self._KafkaInteractor__get_message_batch(consumer)
                if len(message_batch) != 0:
                    break

            for final_message in message_batch:              
            
                checker = json.loads(copy.deepcopy(final_message[1]))
                
                if network_name == "audio":
                    self.Transcreve(final_message,get_key, verbose)
                
                empty = False
            
            consumer.close()

            return empty

        except Exception as e:
            raise Exception(f'{e}.\nErro durante o processo de filtragem das mensagens.')
    
    
    def Transcreve(self, message, get_key=False, verbose=False):
        """
        Método faz a transcrição das mensagens de audio passadas a ele pela fila e envia para a fila resultado ou trata os possiveis erros e casos de descarte que podem ocorrer
        
        """
        
        AD_FIELDS = ['idt_coleta','mensagem_id','tipo', 'criado_em', 'datalake']
        
        PLATFORM = 'telegram'
        AD_TYPE = 'audio'
        
        trash_message = ""
        ad_msg = ""
        
        destined_message = json.loads(copy.deepcopy(message[1]))
        r = sr.Recognizer()
        
        try:
            caminho = "/data/"+destined_message['datalake'][+24:]
            os.system("ffmpeg -i {0} /data/temp.wav > /dev/null 2>&1".format(caminho))
            
            if not(os.path.exists("/data/temp.wav")):
                raise Exception
                
        except Exception as u:
            trash_motive = "Erro na conversão."
            trash_message = self.__get_message(destined_message, AD_FIELDS, AD_TYPE, PLATFORM, trash_motive)
            self.__send_to_trash(trash_message, message[0], get_key, verbose, "erro")
            return

        with sr.AudioFile("/data/temp.wav") as source:
            audio = r.record(source)
            os.remove("/data/temp.wav")
        
        try:
            textoTransc = r.recognize_google(audio, language='pt-BR')
            
            if len(textoTransc) == 0 or textoTransc == None:
                trash_motive = "Mensagem transcrita vazia"
                trash_message = self.__get_message(destined_message, AD_FIELDS, AD_TYPE, PLATFORM, trash_motive)
                self.__send_to_trash(trash_message, message[0], get_key, verbose, "descarte")           
                return
                
            ad_msg = self.__get_message(destined_message, AD_FIELDS, AD_TYPE, PLATFORM, None, textoTransc)
            
            if not  common.publish_kafka_message(self._KafkaInteractor__producer, 
                                                self._KafkaInteractor__write_topics['text_topic_name'],
                                                ad_msg, 
                                                message[0], 
                                                get_key):  


                if verbose : print(common.red_string(f"[{date}] Envio de mensagem falhou"))
                raise Exception("Comunicação com o kafka falhou durante o envio da mensagem.")
                      
            return

        except Exception as e:
            trash_motive = "Erro na transcricao"
            trash_message = self.__get_message(destined_message, AD_FIELDS, AD_TYPE, PLATFORM, trash_motive)
            self.__send_to_trash(trash_message, message[0], get_key, verbose, "erro")           
            return
            
    

    def __send_to_trash(self, message, key, get_key=False, verbose=False, errortype=""):
        """
        Método envia para o lixo ou para o descarte as mensagens que são passadas a ele
        
        """
    
        date = datetime.now()
        if errortype == "erro":
            if not common.publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['error_topic_name'], message,key, get_key):
                if verbose: print(common.red_string(f"[{date}] Envio da mensagem com ERRO para o tópico de erro."))
        elif errortype == "descarte":
            if not common.publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['discard_topic_name'], message,key, get_key):
                if verbose: print(common.red_string(f"[{date}] Mensagem não pode ser enviada para o tópico de descarte."))

    
    def __get_message(self,message, fields, type_format, plataform, trash_motive=None, text=None):
        """
        Método preenche as mensagens que serão enviadas na fila
        
        """
                
        new_message = { indiv_key : message[indiv_key] for indiv_key in fields }
        
        new_message['tipo'] = type_format
        new_message['plataforma'] = plataform
        new_message['ferramenta'] = 'Speech_Recognition'
        new_message['versao_ferramenta'] = '3.8.1'
        
        if trash_motive != None:
            new_message['motivo_descarte'] = trash_motive
        else:
            new_message['texto'] =  text
            
        new_message = json.dumps(new_message)

        
        return new_message  