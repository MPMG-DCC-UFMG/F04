import json
from datetime import datetime
import copy
import os

from common_functions import KafkaInteractor, OffsetAndMetadata
import common_functions as common

ALLOWED_TOPICS = ['texto']
METODOS_POSSIVEIS = ["preliminar", "naive_bayes", "rnn", "han", "lstm"]
METODOS_DEEP_LEARNING = ["rnn", "han", "lstm"]

class IdentificacaoF04(KafkaInteractor):
  
    def __init__(self, configuration_file, outside_docker_models_path, inside_docker_models_path):

        super().__init__(configuration_file)

        self._KafkaInteractor__get_valid_consumers(ALLOWED_TOPICS)

        self.__configuration_file = configuration_file

        self.__metodo_selecionado = self.__configuration_file["metodo_selecionado"]

        self.__outside_docker_models_path = outside_docker_models_path

        self.__inside_docker_models_path = inside_docker_models_path


    '''
    # Se o metodo escolhido for invalido, mandar para a fila de erro (aqui retorna False)
    # Se algum arquivo de configuração não existir, mandar para a fila de erro (aqui retorna False)
    '''
    def is_parametros_validos(self):
        metodo_selecionado = self.__configuration_file["metodo_selecionado"]
        print(metodo_selecionado, f"modelo_{metodo_selecionado}", self.__configuration_file.keys())

        modelo_info = self.__configuration_file[f"modelo_{metodo_selecionado}"]

        print("Dados do modelo selecionado: ", modelo_info)

        if metodo_selecionado not in METODOS_POSSIVEIS:
            print("Parametros invalidos: metodo_selecionado not in METODOS_POSSIVEIS")
            return False

        if metodo_selecionado == "preliminar":
            for filename in [modelo_info["caminho_arquivo_reforco"], modelo_info["caminho_arquivo_pesos"], modelo_info["caminho_arquivo_blacklist"]]:
                # Mudança de nome específica para o Docker. Substitui somente a primeira ocorrência do caminho externo
                filename = filename.replace(self.__outside_docker_models_path, self.__inside_docker_models_path, 1)
                if os.path.isfile(filename) is False:
                    print("Parametros invalidos: metodo_selecionado == preliminar nao tem arquivos validos")
                    print(filename, "nao existe")
                    return False

        if metodo_selecionado == "naive_bayes":
            for filename in [modelo_info["caminho_arquivo_skl"]]:
                # Mudança de nome específica para o Docker. Substitui somente a primeira ocorrência do caminho externo
                filename = filename.replace(self.__outside_docker_models_path, self.__inside_docker_models_path, 1)
                if os.path.isfile(filename) is False:
                    print("Parametros invalidos: metodo_selecionado == naive_bayes nao tem arquivos validos")
                    return False

        if metodo_selecionado in METODOS_DEEP_LEARNING:
            for filename in [modelo_info["caminho_arquivo_npy"], modelo_info["caminho_arquivo_h5"], modelo_info["caminho_arquivo_word2vec"]]:
                # Mudança de nome específica para o Docker. Substitui somente a primeira ocorrência do caminho externo
                filename = filename.replace(self.__outside_docker_models_path, self.__inside_docker_models_path, 1)
                if os.path.isfile(filename) is False:
                    print("Parametros invalidos: metodo_selecionado in METODOS_DEEP_LEARNING nao tem arquivos validos")
                    return False

        return True


    def process_messages(self, topic_id_name, topic_name, get_key=False, verbose=False):
        empty = True

        try:
            consumer = self._KafkaInteractor__connect_kafka_consumer(topic_name, batch_num=10)
            timeout_batch = int(self._KafkaInteractor__timeouts['timeout_batch'])
            message_batch = []

            #A API do Kafka não garante que o método .poll() retornará mensagem apenas da primeira chamada. Para garantir que um tópcio
            #não tem mensagens, é sempre bom chamar várias vezes.            
            for _ in range(5):
                message_batch = consumer.poll(timeout_batch)
                if len(message_batch) != 0:
                    break

            for topic_partition, partition_batch in message_batch.items():
                for message in partition_batch:
                    final_message = (message.key.decode('utf-8'), message.value.decode('utf-8'))

                    parametros_validos = self.is_parametros_validos()

                    if parametros_validos is True:
                        print(">>> os parametros SAO parametros_validos.", flush=True)
                        self.__escreve_score_metodo(final_message, get_key, verbose)

                        consumer.commit({topic_partition: OffsetAndMetadata(message.offset + 1, "no metadata")})

                        empty = False
                    else:
                        print(">>> os parametros NAO SAO parametros_validos.", flush=True)
                        try:
                            consumer.commit({topic_partition: OffsetAndMetadata(message.offset + 1, "no metadata")})
                            consumer.close()
                            motive = f"Erro: Parâmetros do modelo são inválidos"
                            destined_message = json.loads(copy.deepcopy(final_message[1]))
                            destined_message['erro'] = motive
                            self.send_to_error(json.dumps(destined_message), final_message[0], get_key=True)
                        except:
                            pass

                        raise Exception('Erro durante a execução da escrita na fila de erro em F04.')

            consumer.close()

            return empty

        except Exception as e:
            try:
                consumer.commit({topic_partition: OffsetAndMetadata(message.offset + 1, "no metadata")})
                consumer.close()
                motive = f"Erro: {e}"
                destined_message = json.loads(copy.deepcopy(final_message[1]))
                destined_message['erro'] = motive
                self.send_to_error(json.dumps(destined_message), final_message[0], get_key=True)
            except:
                pass

            print(f'{e}.\nErro durante a execução da escrita na fila de erro em F04.')

    def __get_inside_docker_filename(self, original_filename):
        return original_filename.replace(self.__outside_docker_models_path, self.__inside_docker_models_path, 1)

    def __escreve_score_metodo(self, message, get_key=False, verbose=False):
        destined_message = json.loads(copy.deepcopy(message[1]))

        destined_message['metodo_selecionado'] = self.__metodo_selecionado

        print(">>> self.__metodo_selecionado = ", self.__metodo_selecionado)

        print(">>> destined_message = ", destined_message, flush=True)

        try:
            if self.__metodo_selecionado == "preliminar":
                print(">>> entrei em self.__metodo_selecionado == preliminar:", flush=True)

                from metodo_preliminar import MetodoPreliminar
                info_metodo = self.__configuration_file["modelo_preliminar"]

                print(">>> passei por info_metodo  = self.__configuration_file", info_metodo, flush=True)

                # destined_message["caminho_arquivo_reforco"] = info_metodo["caminho_arquivo_reforco"]
                # destined_message["caminho_arquivo_pesos"] = info_metodo["caminho_arquivo_pesos"]
                # destined_message["caminho_arquivo_blacklist"] = info_metodo["caminho_arquivo_blacklist"]
                # destined_message["versao"] = info_metodo["versao"]

                destined_message.update(info_metodo)

                metodoPreliminar= MetodoPreliminar(caminho_arquivo_reforco = self.__get_inside_docker_filename(info_metodo["caminho_arquivo_reforco"]),
                                                   caminho_arquivo_pesos= self.__get_inside_docker_filename(info_metodo["caminho_arquivo_pesos"]),
                                                   caminho_arquivo_blacklist= self.__get_inside_docker_filename(info_metodo["caminho_arquivo_blacklist"]))

                score, mensagem_erro = metodoPreliminar.get_score(texto=destined_message["texto"])

                print("peguei o score: ", score, mensagem_erro, flush=True)
            else:
                print("Comecando o import metodo_aprendizado_maquina...", flush=True)
                from metodo_aprendizado_maquina import MetodoAprendizadoMaquina
                print("Finalizando o import metodo_aprendizado_maquina...", flush=True)

                print(str("modelo_"+self.__metodo_selecionado), f"modelo_{self.__metodo_selecionado}" in self.__configuration_file, flush=True)

                info_metodo = self.__configuration_file[f"modelo_{self.__metodo_selecionado}"]

                print("entrei em NAO preliminar: ", info_metodo, flush=True)

                if self.__metodo_selecionado == "naive_bayes":
                    print("entrei em self.__metodo_selecionado == naive_bayes:", flush=True)
                    caminho_arquivo_modelo = self.__get_inside_docker_filename(info_metodo["caminho_arquivo_skl"])
                    caminho_arquivo_npy = None
                    caminho_arquivo_word2vec = None

                    # destined_message["caminho_arquivo_skl"] = info_metodo["caminho_arquivo_skl"]
                    # destined_message["versao"] = info_metodo["versao"]


                else:
                    caminho_arquivo_modelo = self.__get_inside_docker_filename(info_metodo["caminho_arquivo_h5"])
                    caminho_arquivo_npy = self.__get_inside_docker_filename(info_metodo["caminho_arquivo_npy"])
                    caminho_arquivo_word2vec = self.__get_inside_docker_filename(info_metodo["caminho_arquivo_word2vec"])

                    # destined_message["caminho_arquivo_h5"] = info_metodo["caminho_arquivo_h5"]
                    # destined_message["caminho_arquivo_npy"] = info_metodo["caminho_arquivo_npy"]
                    # destined_message["caminho_arquivo_word2vec"] = info_metodo["caminho_arquivo_word2vec"]
                    # destined_message["versao"] = info_metodo["versao"]

                destined_message.update(info_metodo)

                metodoAM = MetodoAprendizadoMaquina(
                    nome_modelo=self.__metodo_selecionado,
                    caminho_arquivo_modelo=caminho_arquivo_modelo,
                    caminho_arquivo_npy=caminho_arquivo_npy,
                    caminho_arquivo_word2vec=caminho_arquivo_word2vec)

                score, mensagem_erro = metodoAM.get_score(texto=destined_message["texto"])


            date = datetime.now()

            if mensagem_erro is not None:
                motive = f"Erro: {mensagem_erro}"
                destined_message = json.loads(copy.deepcopy(destined_message[1]))
                destined_message['erro'] = motive
                self.send_to_error(json.dumps(destined_message), destined_message[0], get_key=True)
            else:
                destined_message['escore_propaganda_antecipada'] = score

                # TODO se o score is None mandar para fila de erro
                if not common.publish_kafka_message(self._KafkaInteractor__producer,
                                                self._KafkaInteractor__write_topics['result_topic_name'],
                                                json.dumps(destined_message),
                                                message[0],
                                                get_key):


                    if verbose: print(common.red_string(f"[{date}] Envio de mensagem falhou"))
                    self.send_to_trash(destined_message, message[0], get_key, verbose)


        except Exception as e:
            motive = f"Erro: {e}"
            destined_message = json.loads(copy.deepcopy(destined_message[1]))
            destined_message['erro'] = motive
            self.send_to_error(json.dumps(destined_message), destined_message[0], get_key=True)


    def send_to_trash(self, message, key, get_key=False, verbose=False):
        """
        Método que realiza o envio para o tópico de descarte. Isso ocorre se a mensagem estiver no período fornecido no arquivo
        de entrada (ou seja, estiver dentro do período eleitoral).

        """
        date = datetime.now()

        # TODO enviar para a fila de erro ao invés de descarte
        if not common.publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['discard_topic_name'], message,key, get_key):
            if verbose: print(common.red_string(f"[{date}] Envio da mensagem com para o tópico de lixo falhou."))


    def __get_message(self,message, fields, type_format, plataform, trash_motive=None):
                
        new_message = { indiv_key : message[indiv_key] for indiv_key in fields }
        
        new_message['tipo'] = type_format
        new_message['plataforma'] = plataform

        if trash_motive != None:
            new_message['motivo_descarte'] = trash_motive

        new_message = json.dumps(new_message)

        
        return new_message

    def send_to_error(self, message, key, get_key=False, verbose=False):
        date = datetime.now()
        if not common.publish_kafka_message(self._KafkaInteractor__producer, self._KafkaInteractor__write_topics['error_topic_name'], message,key, get_key):
            if verbose: print(common.red_string(f"[{date}] Envio da mensagem com para o tópico de lixo falhou."))
            raise Exception('Mensagem não pode ser enviada para o tópico de erro.')


if __name__ == "__main__":
    pass
