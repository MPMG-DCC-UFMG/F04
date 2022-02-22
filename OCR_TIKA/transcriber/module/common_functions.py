import copy
import subprocess
import json

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka import OffsetAndMetadata
from kafka.admin import KafkaAdminClient, NewTopic

from datetime import datetime
from termcolor import colored


def magenta_string(mstr):
    return colored(str(mstr), 'magenta')

def green_string(mstr):
    return colored(str(mstr), 'green')

def yellow_string(mstr):
    return colored(str(mstr), 'yellow')

def cyan_string(mstr):
    return colored(str(mstr), 'cyan')

def red_string(mstr):
    return colored(str(mstr), 'red')

def publish_kafka_message(producer_instance, topic_name, value, key=0, get_key=False):

    sent = False

    if producer_instance is not None:
        try:
            value_bytes = bytes(value, encoding='utf-8')

            if get_key == True:
                key_bytes = bytes(key, encoding='utf-8')
                producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
            else:
                producer_instance.send(topic_name, value=value_bytes)

            producer_instance.flush()

            sent = True
        except Exception as ex:
            print(f'{ex}.\nException in publishing message.')

    return sent



def systemCommand(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    vet = [ l.decode('utf-8').replace('\n', '') for l in p.stdout.readlines()]
    return vet

class KafkaInteractor:
    def __init__(self, configuration_file):
        try:
            self.__group_name = configuration_file["group_id"]
            
            self.read_topics = configuration_file["read_topics"]
            
            self.__write_topics = configuration_file["write_topics"]

            self.__kafka = configuration_file["kafka_servers"]
            
            self.__producer = self.__connect_kafka_producer()

            self.__timeouts = configuration_file["timeouts"]
            
        except ValueError as e:
            raise ValueError(f'{e}\n.Valor inapropriado para alguma entrada. Checar configurations.json.')

        except Exception as e:
            raise Exception(f'{e}\nErro na leitura e/ou processamento de parâmetros de entrada.')
    
    def __connect_kafka_consumer(self, topicName, batch_num=250):

        _consumer = None
 
        try:
            _consumer = KafkaConsumer(topicName, bootstrap_servers=self.__kafka, api_version=(0, 10), auto_offset_reset='earliest', enable_auto_commit=False, group_id=self.__group_name, max_poll_records=batch_num)
        except Exception as ex:
            raise Exception(f'{ex}.\nException while connecting Kafka.')

        return _consumer

    def __connect_kafka_producer(self):
        """
        Conecta um produtor ao servidor Kafka. A classe base já possui um atributo com um produtor de uso geral, mas mais produtores
        podem ser criados. Um único produtor pode enviar mensagens para diferentes tópicos.

        Parâmetros
        ----------
        
        NULL


        Retorno
        ---------
        _producer : Objeto produtor kafka. 
        
        """

        _producer = None
        try:
            _producer = KafkaProducer(bootstrap_servers=self.__kafka, api_version=(0, 10))
        except Exception as ex:
            print('Exception while connecting Kafka')
            print(str(ex))

        return _producer


    def __get_message_batch(self, consumer):
        """
        Método responsável por recuperar mensagens do tópico passado.
        Retorna uma lista de tuplas, onde cada tupla (chave, mensagem) contém uma mensagem do kafka, além da sua chave de coleta
        da mensagem. 
        
        Parâmetros
        -----------
        consumer: Deverá ser passado um consumidor que interage com o tópico das mensagens.

        Retorno
        -----------
        (list) polled_messages: Lista de tuplas (chave, mensagem).

        """        
        timeout_batch = int(self.__timeouts['timeout_batch'])
        message_batch = consumer.poll(timeout_batch)

        polled_messages = list()
        for topic_partition, partition_batch in message_batch.items():
            for message in partition_batch:
                consumer.commit({topic_partition: OffsetAndMetadata(message.offset+1, "no metadata")})
                final_message = (message.key.decode('utf-8'), message.value.decode('utf-8'))
                polled_messages.append(final_message)

        return polled_messages

    def __get_topic_list(self):
        """
        Método responsável por recuperar a lista de tópicos existentes em um dado servidor Kafka.

        Parâmetros
        ----------
        
        NULL

        
        Retorno
        ----------
        (set) server_topics.
        
        """
        
        kafka_admin = KafkaConsumer(bootstrap_servers=self.__kafka, api_version=(0, 10))
        server_topics = kafka_admin.topics()
        kafka_admin.close()

        return server_topics
            
    def __check_and_create(self, topic_dictionary):
        """
        O método checa se um determinado tópico existe, e caso não exista cria o tópico Kafka para a escrita..
        Foi pensado para funcionar com o dicionário passado no arquivo de entrada (configurations.json), que contém
        um campo 'write_topics' que especifíca o nome dos tópicos que as aplicações escreverão.. Esse método deve ser
        excluído posteriormente.
        
        """
        
        for name, topic_name in topic_dictionary.items():
            if topic_name not in self.__get_topic_list():
                admin_client = KafkaAdminClient(bootstrap_servers=self.__kafka, client_id=self.__group_name)
                topic_list = []
                topic_list.append(NewTopic(name=f"{topic_name}", num_partitions=1, replication_factor=1))
                admin_client.create_topics(new_topics=topic_list, validate_only=False)
                admin_client.close()
   
    def __get_valid_consumers(self, target_networks):
        """
        O método recebe uma lista contendo o nome das redes de interesse, e as busca dentre as opções passadas no campo
        'read_topics' no configurations.json... 
        """ 
        
        
        yorn = None
        exclude_list = list()

        for topic, net in self.read_topics.items():
            
            if net not in target_networks:
                exclude_list.append(topic)
                continue

            yorn = True if topic in self.__get_topic_list() else False
            
            if yorn == False:
                raise Exception(f'A existência do tópico {topic} da rede {net} não foi detectada. Confira a entrada.')


        for item in exclude_list:
            del self.read_topics[item]


        if len(self.read_topics) == 0:
            raise Exception(f'Todos os tópicos de leitura foram excluídos devido à alguma anormalidade. Confira a entrada.')      


if __name__ == '__main__':
    pass