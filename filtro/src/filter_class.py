import json
from datetime import datetime
import copy

from common_functions import KafkaInteractor, OffsetAndMetadata
import common_functions as common


ALLOWED_NETWORKS = ['twitter', 'telegram']

def transform_target_date(target_date):
    nss = target_date.split('-')
    final_string = f'{nss[2]}-{nss[1]}-{nss[0]}'
    return final_string



def check_date(target_date, all_dates):
    
    target_date = str(target_date)
    
    answer = False

    for dates in all_dates:
        for date_min, date_max in dates.items():

            if date_min != None and date_max != None: 

                answer = date_min <= target_date <= date_max

        if answer == True:
            break        
    
    return answer

def transform_datas(data_list):
    list_cole = []
    dict_cole = {}
    for item in data_list:
        for key,value in item.items():
            data_min = key.split(':')[1]
            
            data_min = transform_target_date(data_min)
            
            data_max = value.split(':')[1]
            
            data_max = transform_target_date(data_max)
            
            dict_cole[data_min] = data_max
            
            list_cole.append(dict_cole)            
        dict_cole = {}
    return list_cole
    
class Filter(KafkaInteractor):  
  
    def __init__(self, configuration_file):

        super().__init__(configuration_file)

        self._KafkaInteractor__get_valid_consumers(ALLOWED_NETWORKS)

        self.__texto = configuration_file["filtro_texto"] if "filtro_texto" in configuration_file else True
        
        self.__imagem = configuration_file["filtro_imagem"] if "filtro_imagem" in configuration_file else True
        
        self.__audio = configuration_file["filtro_audio"] if "filtro_audio" in configuration_file else True

        self.__datas = transform_datas(configuration_file["datas"]) if "datas" in configuration_file else []        


    def filter_messages(self, network_name, topic_name, get_key=False, verbose=False):
        empty = True

        #Remove os warnings :P
        consumer = None
        message_batch = None
        try:
            consumer = self._KafkaInteractor__connect_kafka_consumer(topic_name)
            timeout_batch = int(self._KafkaInteractor__timeouts['timeout_batch'])*10
            #A API do Kafka não garante que o método .poll() retornará mensagem apenas da primeira chamada. Para garantir que um tópcio
            #não tem mensagens, é sempre bom chamar várias vezes.            
            for _ in range(2):
                message_batch = consumer.poll(timeout_batch)
                if len(message_batch) != 0:
                    break
                    
            for topic_partition, partition_batch in message_batch.items():
                for message in partition_batch:
                    final_message = (message.key.decode('utf-8'), message.value.decode('utf-8'))
                    
                    if network_name == 'twitter':
                        self.__twitter_messages(final_message, get_key, verbose)

                    elif network_name == "telegram":
                        self.__telegram_messages(final_message,get_key, verbose)

                    consumer.commit({topic_partition: OffsetAndMetadata(message.offset+1, "no metadata")})
                    
                    empty = False
            
            consumer.close()

            return empty

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

            raise Exception(f'{e}.\nErro durante o processo de filtragem das mensagens.')
    
    def __twitter_messages(self, message, get_key=False, verbose=False):
        """
        Método que realiza a classificação das mensagens do tópico de post do twitter, e as envia de acordo para o tópico
        de imagens e F04.

        Parâmetros
        ----------
        (tuple) message: Contém a tupla de (chave, mensagem) que pode ser obtida através da chamada do método de get_batch_messages.

        Retorno
        ----------
        NULL
        
        """
        TEXT_FIELDS = [key for key, _ in message.items()]
        IMAGE_FIELDS = ['identificador', 'id_do_autor', 'midias']

        PLATFORM = 'twitter'
        TEXT_TYPE = 'texto'
        IMG_TYPE = 'imagem'

        img_msg = ""
        destined_message = json.loads(copy.deepcopy(message[1]))
        midia_count = len(destined_message["midias"])
        date = datetime.now()

        if check_date(destined_message["criado_em"], self.__datas):
            
            tipo = 'texto' if midia_count == 0 else 'texto+imagem'
            
            trash_motive = "Tweet fora do periodo valido para analise."

            trash_message = self.__get_message(destined_message, TEXT_FIELDS, tipo, PLATFORM, trash_motive)

            self.send_to_trash(trash_message, message[0], get_key, verbose)
            return

        if midia_count != 0:
            if self.__imagem:
                
                img_msg = self.__get_message(destined_message, IMAGE_FIELDS, IMG_TYPE, PLATFORM)
                
                if not common.publish_kafka_message(self._KafkaInteractor__producer, 
                                            self._KafkaInteractor__write_topics['image_topic_name'],
                                            img_msg, 
                                            message[0], 
                                            get_key):  
            
                
                    if verbose : print(common.red_string(f"[{date}] Envio de mensagem falhou"))
                    raise Exception("Comunicação com o kafka falhou durante o envio da mensagem.")
            
            else:
                trash_motive = "Parametro filtro_imagem configurado como falso no arquivo de configuraçao."
                
                trash_message = self.__get_message(destined_message, IMAGE_FIELDS, IMG_TYPE, PLATFORM, trash_motive)
                
                self.send_to_trash(trash_message, message[0], get_key, verbose)



        if self.__texto:
            if destined_message['texto'] == "":
                trash_motive = "Campo de texto do tweet vazio."
                trash_message = self.__get_message(destined_message, TEXT_FIELDS, TEXT_TYPE, PLATFORM, trash_motive)
                self.send_to_trash(trash_message, message[0], get_key, verbose)
            
            else:
                final_text_message = self.__get_message(destined_message, TEXT_FIELDS, TEXT_TYPE, PLATFORM)

                if not common.publish_kafka_message(self._KafkaInteractor__producer, 
                                                self._KafkaInteractor__write_topics['text_topic_name'], 
                                                final_text_message, 
                                                message[0], 
                                                get_key):

                    
                    if verbose: print(common.red_string(f"[{date}] Envio de mensagem falhou"))
                    raise Exception("Comunicação com o kafka falhou durante o envio da mensagem.")
        else:
            
            trash_motive = "Parametro filtro_texto configurado como falso no arquivo de configuracao."
            
            trash_message = self.__get_message(destined_message, TEXT_FIELDS, TEXT_TYPE, PLATFORM, trash_motive)
            
            self.send_to_trash(trash_message, message[0], get_key, verbose)
                       

    def __telegram_messages(self, message, get_key=False, verbose=False):

        TEXT_FIELDS = ['idt_coleta','mensagem_id','tipo', 'criado_em', 'texto']
        MEDIA_FIELDS = ['idt_coleta','mensagem_id','tipo', 'criado_em', 'datalake']

        PLATFORM = 'telegram'
        TEXT_TYPE = 'texto'
        IMG_TYPE = 'imagem'
        AD_TYPE = 'audio'
            
        trash_message = ""
        ad_msg = ""
        img_msg = ""
        destined_message = json.loads(copy.deepcopy(message[1]))
        


        if check_date(destined_message["criado_em"], self.__datas):
            trash_motive = "Mensagem fora do período valido para analise."
            if destined_message["tipo"] == "video" or destined_message["tipo"] == "other":
                tipo = "texto"
                trash_message = self.__get_message(destined_message, TEXT_FIELDS, tipo, PLATFORM, trash_motive)
            elif destined_message["tipo"] == "image":
                if destino_message["arquivo"] == "null":
                    trash_motive = "sem arquivo"
                    trash_message = self.__get_message(destined_message, TEXT_FIELDS, tipo, PLATFORM, trash_motive)
                    self.send_to_trash(trash_message, message[0], get_key, verbose)
                    return	
                tipo = "texto+imagem"
                trash_message = self.__get_message(destined_message, MEDIA_FIELDS, tipo, PLATFORM, trash_motive)
            elif destined_message["tipo"] == "audio":
                if destino_message["arquivo"] == "null":
                    trash_motive = "sem arquivo"
                    trash_message = self.__get_message(destined_message, TEXT_FIELDS, tipo, PLATFORM, trash_motive)
                    self.send_to_trash(trash_message, message[0], get_key, verbose)
                    return
                tipo = "audio"   
                trash_message = self.__get_message(destined_message, MEDIA_FIELDS, tipo, PLATFORM, trash_motive)
            else:
                tipo = "desconhecido"
                trash_message = self.__get_message(destined_message, TEXT_FIELDS, tipo, PLATFORM, trash_motive)
            
            self.send_to_trash(trash_message, message[0], get_key, verbose)
            return

        if destined_message["tipo"] == "audio":
            if self.__audio:
                ad_msg = self.__get_message(destined_message, MEDIA_FIELDS, AD_TYPE, PLATFORM)
            else:
                trash_motive = "Parametro filtro_audio configurado como falso no arquivo de configuracao."           
                trash_message = self.__get_message(destined_message, MEDIA_FIELDS, AD_TYPE, PLATFORM, trash_motive)            
                self.send_to_trash(trash_message, message[0], get_key, verbose)
        
        if destined_message["tipo"] == "image" and self.__imagem:
            if self.__imagem:
                img_msg = self.__get_message(destined_message, MEDIA_FIELDS, IMG_TYPE, PLATFORM)
            else:
                trash_motive = "Parametro filtro_imagem configurado como falso no arquivo de configuracao."           
                trash_message = self.__get_message(destined_message, MEDIA_FIELDS, IMG_TYPE, PLATFORM, trash_motive)            
                self.send_to_trash(trash_message, message[0], get_key, verbose)

        date = datetime.now()

        if ad_msg:
            if not  common.publish_kafka_message(self._KafkaInteractor__producer, 
                                                self._KafkaInteractor__write_topics['audio_topic_name'],
                                                ad_msg, 
                                                message[0], 
                                                get_key):  


                if verbose : print(common.red_string(f"[{date}] Envio de mensagem falhou"))
                raise Exception("Comunicação com o kafka falhou durante o envio da mensagem.")
        
        else:
            if img_msg:
                if not  common.publish_kafka_message(self._KafkaInteractor__producer, 
                                                     self._KafkaInteractor__write_topics['image_topic_name'],
                                                     img_msg, 
                                                     message[0], 
                                                     get_key):  


                    if verbose : print(common.red_string(f"[{date}] Envio de mensagem falhou"))
                    raise Exception("Comunicação com o kafka falhou durante o envio da mensagem.")
            
            if self.__texto:
                if destined_message['texto'] == "":
                    trash_motive = "Campo de texto da mensagem vazio."
                    trash_message = self.__get_message(destined_message, TEXT_FIELDS, TEXT_TYPE, PLATFORM, trash_motive)
                    self.send_to_trash(trash_message, message[0], get_key, verbose)
                else:
                    final_text_message = self.__get_message(destined_message, TEXT_FIELDS, TEXT_TYPE, PLATFORM)


                    if not common.publish_kafka_message(self._KafkaInteractor__producer, 
                                                    self._KafkaInteractor__write_topics['text_topic_name'], 
                                                    final_text_message, 
                                                    message[0], 
                                                    get_key):


                        if verbose: print(common.red_string(f"[{date}] Envio de mensagem falhou"))
                        raise Exception("Comunicação com o kafka falhou durante o envio da mensagem.")
            else:
            
                trash_motive = "Parametro filtro_texto configurado como falso no arquivo de configuracao."           
                trash_message = self.__get_message(destined_message, TEXT_FIELDS, TEXT_TYPE, PLATFORM, trash_motive)            
                self.send_to_trash(trash_message, message[0], get_key, verbose)


    def send_to_trash(self, message, key, get_key=False, verbose=False):
        """
        Método que realiza o envio para o tópico de descarte. Isso ocorre se a mensagem estiver no período fornecido no arquivo
        de entrada (ou seja, estiver dentro do período eleitoral).
        
        
        """
        date = datetime.now()
        if not common.publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['discard_topic_name'], message,key, get_key):
            if verbose: print(common.red_string(f"[{date}] Envio da mensagem para o tópico falhou."))
            raise Exception('Mensagem não pode ser enviada para o tópico de descarte.')

    def __send_to_error(self, message, key, get_key=False, verbose=False):
        date = datetime.now()
        if not common.publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['error_topic_name'], message,key, get_key):
            if verbose: print(common.red_string(f"[{date}] Envio da mensagem com para o tópico de lixo falhou."))
            raise Exception('Mensagem não pode ser enviada para o tópico de erro.')

    def __get_message(self,message, fields, type_format, plataform, trash_motive=None):
                
        new_message = { indiv_key : message[indiv_key] for indiv_key in fields }
        
        new_message['tipo'] = type_format
        new_message['plataforma'] = plataform

        if trash_motive != None:
            new_message['motivo_descarte'] = trash_motive

        new_message = json.dumps(new_message)

        
        return new_message       
  
    def __get_audio_message(self,message):
        TELEGRAM_FIELDS = ['identificador', 'mensagem_id', 'enviada_por', 'datalake']
                
        audio_message = { indiv_key : message[indiv_key] for indiv_key in TELEGRAM_FIELDS }
        
        audio_message['tipo'] = 'audio'
        audio_message = json.dumps(audio_message)
        
        return audio_message 



if __name__ == "__main__":
    pass
