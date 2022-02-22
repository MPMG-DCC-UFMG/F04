#!/usr/bin/python

import sys
import os
from datetime import datetime

print("Passei 1 em metodo_preliminar", flush=True)

import re
print("Passei 2 em metodo_preliminar", flush=True)
import spacy
print("Passei 3 em metodo_preliminar", flush=True)
import json

print("Passei 2 em metodo_preliminar", flush=True)

import argparse
import logging

from collections import Counter
from datetime import datetime

from numpy import std

print("Terminei de importar principais libs em metodo_preliminar", flush=True)

nlp = spacy.load("pt_core_news_sm")

print("Terminei de importar spacy lib em metodo_preliminar", flush=True)

PALAVRAS_REFORCO = []
TERMOS_SELECIONADOS = {}
BLACKLIST = []

TIPO_COMBINACAO_LINEAR = "combinacao-linear"
TIPO_COMBINACAO_MAXIMO = "maximo"
TIPO_COMBINACAO_STD = "desvio-padrao"

print("Terminei de importar metodo_preliminar", flush=True)

class MetodoPreliminar:
    def __init__(self, caminho_arquivo_reforco, caminho_arquivo_pesos, caminho_arquivo_blacklist):
        self.__caminho_arquivo_reforco = caminho_arquivo_reforco
        self.__caminho_arquivo_pesos = caminho_arquivo_pesos
        self.__caminho_arquivo_blacklist = caminho_arquivo_blacklist


    def __carrega_arquivos_de_configuracao(self):
        try:
            with open(self.__caminho_arquivo_reforco, "r", encoding="utf-8") as file_input:
                for document in file_input:
                    document = json.loads(document)
                    PALAVRAS_REFORCO.append((document["palavra_original"], document["nova_palavra"]))

            with open(self.__caminho_arquivo_pesos, "r", encoding="utf-8") as file_input:
                for document in file_input:
                    document = json.loads(document)
                    TERMOS_SELECIONADOS[document["palavra"]] = document["peso"]

            with open(self.__caminho_arquivo_blacklist, "r", encoding="utf-8") as file_input:
                for termo in file_input:
                    termo = self.__faz_limpeza_texto(text=termo)
                    BLACKLIST.append(termo)

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)

            return False

    def __get_texto_sem_simbolos_especiais(self, text):
        try:
            text = text.lower()

            text = text.replace('\n', " ").replace('\"', "").replace('"', "").replace('\'', "").replace("'", "").replace(",", " ").replace(":","").replace(".", "").replace(";", "").replace("!", "").replace("$", "").replace("%", "").replace("&", "").replace("?", "").replace("*", "").replace("-", " ").replace("(", "").replace(")", "").replace("+", "")

            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)

            return None

    def __get_texto_sem_marcacoes_especiais(self, text):
        try:
            ### remove espaços desnecessários e quebras de linha
            my_val = str(text).rstrip("\n").rstrip("\t").rstrip("\r")
            my_val = str(my_val).replace('\r', " ").replace('\n', " ").replace('\t', " ")
            text = my_val.strip()

            ### remove emojis
            text = ' '.join(re.split("[^a-z|0-9|á|é|í|ó|ú|â|ê|î|ô|û|ã|õ|à|ç|/|ü]+", text))

            ### substitui urls, hashtags e menções por termos apropriados
            text = 'link'.join(re.split("http\S+", text))
            text = 'hashtag'.join(re.split("#\S+",text))
            text = 'arroba'.join(re.split("@\S+",text))
            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)
            return None

    def __get_texto_reforcado(self, text):
        try:
            ### Substitui palavras por palavras de reforço da lista
            for palavra_info in PALAVRAS_REFORCO:
                text = (" " + text + " ").replace(" " + palavra_info[0] + " ", " " + palavra_info[1] + " ")
                text = (" " + text + " ").replace(" @" + palavra_info[0] + " ", " " + palavra_info[1] + " ")
                text = text[1:len(text) - 1]

            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)
            return None


    def __get_texto_lematizado(self, text):
        try:
            doc = nlp(text)
            text = ' '.join([token.lemma_ for token in doc])

            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)
            return None


    def __faz_limpeza_texto(self, text):
        try:
            text = self.__get_texto_sem_simbolos_especiais(text=text)
            text = self.__get_texto_reforcado(text=text)
            text = self.__get_texto_sem_marcacoes_especiais(text=text)
            text = self.__get_texto_lematizado(text=text)

            return text, None
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)
            return None, e

    def __get_normalized_value(self, value, max_value, min_value):
        normalized = (value - min_value) / (max_value - min_value)

        return normalized

    def __desvio_padrao(self, string_list):
        term_metric_list = []
        explicacao_texto = ""
        explicacao_final = TIPO_COMBINACAO_STD+": "
        for palavra in string_list:
            term_metric_list.append(TERMOS_SELECIONADOS[palavra])
            explicacao_texto += "{" + palavra + ":" + str(round(TERMOS_SELECIONADOS[palavra], 3)) + "} "

        score = std(term_metric_list)

        explicacao_texto = explicacao_final + explicacao_texto

        return score, explicacao_texto

    def __combinacao_linear(self, string_list):
        score = 0
        explicacao_texto = ""
        explicacao_final = TIPO_COMBINACAO_LINEAR+": "
        for palavra in string_list:
            score += TERMOS_SELECIONADOS[palavra]
            explicacao_texto += "{" + palavra + ":" + str(round(TERMOS_SELECIONADOS[palavra], 3)) + "} "

        explicacao_texto = explicacao_final + explicacao_texto

        return score, explicacao_texto

    def __maximo(self, string_list):
        score = 0
        explicacao_texto = ""
        explicacao_final = TIPO_COMBINACAO_MAXIMO + ": "
        for palavra in string_list:
            if TERMOS_SELECIONADOS[palavra] > score:
                score = TERMOS_SELECIONADOS[palavra]
            explicacao_texto += "{" + palavra + ":" + str(round(TERMOS_SELECIONADOS[palavra], 3)) + "} "

        explicacao_texto = explicacao_final + explicacao_texto

        return score, explicacao_texto

    '''
    Retorno:  score, explicacao_texto, mensagem_erro
    '''
    def __get_method_score(self, text, tipo_combinacao):
        try:
            string_list = text.split(" ")

            ### Filtra somente as palavras que estão nos termos considerados
            string_list = list(filter(lambda x: x in TERMOS_SELECIONADOS, string_list))

            # combinacao linear, max, standard deviation
            if tipo_combinacao == TIPO_COMBINACAO_LINEAR:
                score, explicacao_texto = self.__combinacao_linear(string_list=string_list)
            elif tipo_combinacao == TIPO_COMBINACAO_MAXIMO:
                score, explicacao_texto = self.__maximo(string_list=string_list)
            else:
                score, explicacao_texto = self.__desvio_padrao(string_list=string_list)

            ### Se a soma dos valores normalizados do metodo for maior que 1, então score = 1
            score = 1 if score > 1 else score

            return score, explicacao_texto, None
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)
            return None, None, e

    '''
    Retorno:  presenca_blacklist, mensagem_erro
    '''
    def __verifica_presenca_em_blacklist(self, text, blacklist_extra=None):
        try:
            text = self.__faz_limpeza_texto(text=text)

            for termo in BLACKLIST:
                if termo in text:
                    return True, None

            if blacklist_extra is not None:
                for termo in blacklist_extra:
                    termo = self.__faz_limpeza_texto(text=termo)

                    if termo in text:
                        return True, None

            return False, None
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)
            return None, e

    '''
    Retorno:  score, mensagem_erro
    '''
    def __get_resultado(self, text, blacklist_extra, tipo_combinacao):
        try:
            if text is not None and len(text) > 0:
                #### Verifica se texto contem termos da blacklist
                result, mensagem_erro = self.__verifica_presenca_em_blacklist(text=text, blacklist_extra=blacklist_extra)

                if mensagem_erro is not None:
                    return None, mensagem_erro

                if result is True:
                    score = 0
                    return (score, None)
                else:
                    text, mensagem_erro = self.__faz_limpeza_texto(text=text)

                    if mensagem_erro is not None:
                        return None, mensagem_erro

                    score, explicacao_texto, mensagem_erro = self.__get_method_score(text=text, tipo_combinacao=tipo_combinacao)

                    if mensagem_erro is not None:
                        return None, mensagem_erro

                    score = round(score, 3)

                    return score, None

            else:
                # print("ERRO: texto nulo ou vazio.", flush=True)
                return(None, "Texto nulo ou vazio.")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
                  '\tData e Hora: ',
                  datetime.now(),
                  flush=True)
            return (None, e)

    '''
    Retorno:  data, mensagem_erro
    '''
    def __get_objeto_data(self, string_datetime, only_date=False):
        a_datetime = None
        string_datetime = string_datetime.replace("\"", "")
        string_datetime = string_datetime.replace("'", "")

        if only_date is True:
            datetime_patterns = ['%d-%m-%Y', '%Y-%m-%d']
        else:
            datetime_patterns = ['%Y-%m-%d %H:%M:%S','%Y-%m-%dT%H:%M:%SZ', '%a %b %d %H:%M:%S +0000 %Y']

        for datetime_pattern in datetime_patterns:
            try:
                a_datetime = datetime.strptime(string_datetime, datetime_pattern)
            except Exception as e:
                # print("ERRO ao formatar string como DATA:", string_datetime, "DETALHES:", e, flush=True)
                pass
            else:
                return (a_datetime.date(), None)

        if a_datetime is None:
            return (None, str("ERRO ao formatar string como DATA: {}".format(string_datetime)))

    def __processa_documento_json(self,document, atributo_texto,blacklist_extra, tipo_combinacao):

        self.__get_resultado(text=document[atributo_texto], blacklist_extra=blacklist_extra, tipo_combinacao=tipo_combinacao)

    '''
    Retorno:  score, mensagem_erro
    '''
    def get_score(self,texto):
        ### Carrega arquivos de configuração na memória
        retorno = self.__carrega_arquivos_de_configuracao()

        if retorno is False:
            mensagem_erro = "Falha no carregamento dos arquivos de configuração"
            return (None, mensagem_erro)

        ### Define a técnica de combinação padrão
        ### Parametro tipo_combinacao é utilizado para testes e validação
        # tipo_combinacao = TIPO_COMBINACAO_LINEAR if args.tipo_combinacao is False else args.tipo_combinacao

        tipo_combinacao = TIPO_COMBINACAO_LINEAR

        '''
        #DETERMINA TIPO DE ENTRADA
        '''
        #### texto único
        score, mensagem_erro = self.__get_resultado(text=texto, blacklist_extra=None,
                        tipo_combinacao=tipo_combinacao)

        return (score, mensagem_erro)