#!/usr/bin/python

import sys
import os
from datetime import datetime

import re
import spacy
import json

import argparse
import logging

from collections import Counter
from datetime import datetime

from numpy import std

nlp = spacy.load("pt_core_news_lg")

PALAVRAS_REFORCO = []
TERMOS_SELECIONADOS = {}
BLACKLIST = []

TIPO_COMBINACAO_LINEAR = "combinacao-linear"
TIPO_COMBINACAO_MAXIMO = "maximo"
TIPO_COMBINACAO_STD = "desvio-padrao"

def __carrega_arquivos_de_configuracao():
    try:
        with open("reforco.json", "r", encoding="utf-8") as file_input:
            for document in file_input:
                document = json.loads(document)
                PALAVRAS_REFORCO.append((document["palavra_original"], document["nova_palavra"]))

        with open("pesos.json", "r", encoding="utf-8") as file_input:
            for document in file_input:
                document = json.loads(document)
                TERMOS_SELECIONADOS[document["palavra"]] = document["peso"]

        with open("blacklist.txt", "r", encoding="utf-8") as file_input:
            for termo in file_input:
                termo = __faz_limpeza_texto(text=termo)
                BLACKLIST.append(termo)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
              '\tData e Hora: ',
              datetime.now(),
              flush=True)

def __get_texto_sem_simbolos_especiais(text):
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

def __get_texto_sem_marcacoes_especiais(text):
    try:
        ### remove espa??os desnecess??rios e quebras de linha
        my_val = str(text).rstrip("\n").rstrip("\t").rstrip("\r")
        my_val = str(my_val).replace('\r', " ").replace('\n', " ").replace('\t', " ")
        text = my_val.strip()

        ### remove emojis
        text = ' '.join(re.split("[^a-z|0-9|??|??|??|??|??|??|??|??|??|??|??|??|??|??|/|??]+", text))

        ### substitui urls, hashtags e men????es por termos apropriados
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

def __get_texto_reforcado(text):
    try:
        ### Substitui palavras por palavras de refor??o da lista
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


def __get_texto_lematizado(text):
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


def __faz_limpeza_texto(text):
    try:
        text = __get_texto_sem_simbolos_especiais(text=text)
        text = __get_texto_reforcado(text=text)
        text = __get_texto_sem_marcacoes_especiais(text=text)
        text = __get_texto_lematizado(text=text)

        return text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
              '\tData e Hora: ',
              datetime.now(),
              flush=True)

def __get_normalized_value(value, max_value, min_value):
    normalized = (value - min_value) / (max_value - min_value)

    return normalized

def __desvio_padrao(string_list):
    term_metric_list = []
    explicacao_texto = ""
    explicacao_final = TIPO_COMBINACAO_STD+": "
    for palavra in string_list:
        term_metric_list.append(TERMOS_SELECIONADOS[palavra])
        explicacao_texto += "{" + palavra + ":" + str(round(TERMOS_SELECIONADOS[palavra], 3)) + "} "

    score = std(term_metric_list)

    explicacao_texto = explicacao_final + explicacao_texto

    return score, explicacao_texto

def __combinacao_linear(string_list):
    score = 0
    explicacao_texto = ""
    explicacao_final = TIPO_COMBINACAO_LINEAR+": "
    for palavra in string_list:
        score += TERMOS_SELECIONADOS[palavra]
        explicacao_texto += "{" + palavra + ":" + str(round(TERMOS_SELECIONADOS[palavra], 3)) + "} "

    explicacao_texto = explicacao_final + explicacao_texto

    return score, explicacao_texto

def __maximo(string_list):
    score = 0
    explicacao_texto = ""
    explicacao_final = TIPO_COMBINACAO_MAXIMO + ": "
    for palavra in string_list:
        if TERMOS_SELECIONADOS[palavra] > score:
            score = TERMOS_SELECIONADOS[palavra]
        explicacao_texto += "{" + palavra + ":" + str(round(TERMOS_SELECIONADOS[palavra], 3)) + "} "

    explicacao_texto = explicacao_final + explicacao_texto

    return score, explicacao_texto

def __get_method_score(text, tipo_combinacao):
    try:
        string_list = text.split(" ")

        ### Filtra somente as palavras que est??o nos termos considerados
        string_list = list(filter(lambda x: x in TERMOS_SELECIONADOS, string_list))

        # combinacao linear, max, standard deviation
        if tipo_combinacao == TIPO_COMBINACAO_LINEAR:
            score, explicacao_texto = __combinacao_linear(string_list=string_list)
        elif tipo_combinacao == TIPO_COMBINACAO_MAXIMO:
            score, explicacao_texto = __maximo(string_list=string_list)
        else:
            score, explicacao_texto = __desvio_padrao(string_list=string_list)

        ### Se a soma dos valores normalizados do metodo for maior que 1, ent??o score = 1
        score = 1 if score > 1 else score

        return score, explicacao_texto
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
              '\tData e Hora: ',
              datetime.now(),
              flush=True)

def __verifica_presenca_em_blacklist(text, blacklist_extra=None):
    try:
        text = __faz_limpeza_texto(text=text)

        for termo in BLACKLIST:
            if termo in text:
                return True

        if blacklist_extra is not None:
            for termo in blacklist_extra:
                termo = __faz_limpeza_texto(text=termo)

                if termo in text:
                    return True

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
              '\tData e Hora: ',
              datetime.now(),
              flush=True)

def __imprime_resultado(text, blacklist_extra, explicacao, tipo_combinacao):
    try:
        if text is not None and len(text) > 0:
            #### Verifica se texto contem termos da blacklist
            result = __verifica_presenca_em_blacklist(text=text, blacklist_extra=blacklist_extra)
            if result is True:
                score = 0
                explicacao_texto = ""
            else:
                text = __faz_limpeza_texto(text=text)

                score, explicacao_texto = __get_method_score(text=text, tipo_combinacao=tipo_combinacao)

                score = round(score, 3)

            if explicacao is True:
                print(score,"\tExplicacao: ", explicacao_texto, flush=True)
            else:
                print(score, flush=True)
        else:
            print("ERRO: texto nulo ou vazio.", flush=True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
              '\tData e Hora: ',
              datetime.now(),
              flush=True)


def __get_objeto_data(string_datetime, only_date=False):
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
            return (a_datetime.date())

    if a_datetime is None:
        print("ERRO ao formatar string como DATA:", string_datetime, flush=True)

        return (None)

def __processa_documento_json(document, atributo_texto, atributo_data, data_minima, data_maxima, blacklist_extra,
                              explicacao, tipo_combinacao):
    if atributo_texto in document and atributo_data in document:
        data_documento = __get_objeto_data(string_datetime=document[atributo_data])

        if data_documento >= data_minima and data_documento <= data_maxima:
            __imprime_resultado(text=document[atributo_texto], blacklist_extra=blacklist_extra, explicacao=explicacao,
                                tipo_combinacao=tipo_combinacao)
    else:
        print("ERRO: documento nao possui atributo de texto ou atributo de data.")


def main():
    try:
        parser = argparse.ArgumentParser(description='Metodo para identificar propagandas eleitorais.')

        '''
        ###############
        PARAMETROS OBRIGAT??RIOS
        ###############
        '''
        #### texto ??nico --- OU
        parser.add_argument('--texto',dest='text', type=str, default=False,
                            help='Texto para ser avaliado.')
        #### lista de JSON --- OU
        parser.add_argument('--lista',  dest='json_list', type=str, default=False,
                            help='Lista no formato JSON com os documentos.')
        #### corpus JSON ou TXT (por padr??o, o corpus ?? JSON)
        parser.add_argument('--arquivo', dest='filename_corpus', type=str, default=False,
                            help='Caminho do arquivo que contem o corpus.')
        #### --- Se corpus tipo JSON:
        parser.add_argument('--atributo-texto', dest='attribute_name_text', type=str, default=False,
                            help='Nome do atributo no JSON que contem o texto.')
        parser.add_argument('--atributo-data', dest='attribute_name_date', type=str, default=False,
                            help='Nome do atributo no JSON que contem o texto.')
        parser.add_argument('--data-inicial',  dest='date_min', type=str, default=False,
                            help='Data inicial para a filtragem (limite inferior).')
        parser.add_argument('--data-final', dest='date_max', type=str, default=False,
                            help='Data final para a filtragem (limite superior).')

        #### --- Se corpus tipo TXT:
        parser.add_argument('-txt',action='store_true', dest='corpus_txt', default=False,
                            help='Declara que tipo do corpus como TXT')

        #### --- Se corpus tipo JSON:
        parser.add_argument('-json', action='store_true', dest='corpus_json', default=False,
                            help='Declara que tipo do corpus como JSON')

        ### ---- Op????o para imprimir a explica????o do score
        parser.add_argument('-explicacao', action='store_true', dest='explicacao_metodo', default=False,
                            help='Mostra a explicacao de cada score')

        '''
        ###############
        PARAMETROS OPCIONAIS
        ###############
        '''
        parser.add_argument('--blacklist-arquivo', '-ba', dest='filename_blacklist', type=str, default=False,
                            help='Caminho do arquivo que contem termos para acrescentar na blacklist.')
        parser.add_argument('--blacklist-texto', '-bt', dest='blacklist_text', type=str, default=False,
                            help='Texto que contem termos para acrescentar na blacklist.')

        ### Parametro tipo_combinacao ?? utilizado para testes e valida????o
        # parser.add_argument('-combinacao', dest='tipo_combinacao', type=str, default=False,
        #                     help='Tipo de combinacao utilizada no metodo ({}, {}, {}).'.format(TIPO_COMBINACAO_LINEAR,TIPO_COMBINACAO_MAXIMO, TIPO_COMBINACAO_STD))

        '''
        ###############
        PROCESSA PARAMETROS DE PROGRAMA E VERIFICA ERROS
        ###############
        '''
        args = parser.parse_args()


        ### --- Verifica se foi informado um parametro de entrada
        if (args.text is False and args.filename_corpus is False and args.json_list is False):
            parser.error('Metodo precisa de um tipo de entrada (--texto, --lista, --arquivo)')
        ### --- Verifica se o formato do arquivo foi informado caso a entrada seja um arquivo (texto ou json)
        elif (args.filename_corpus and (args.corpus_json is False and args.corpus_txt is False)):
            parser.error(
                'O parametro --arquivo exige que seja informado o formato da entrada (-txt ou -json)')
        ### --- Verifica se entrada em formato JSON possui todos os par??metros obrigat??rios
        elif (((args.filename_corpus and args.corpus_json) or args.json_list) and
                  (args.attribute_name_text is False or args.attribute_name_date is False or
                           args.date_min is False or args.date_max is False)):
            nome_parametro = "--arquivo" if args.filename_corpus else "--lista"
            parser.error('O parametro {} exige que seja informado --atributo-texto, --atributo-data, --data-inicial e --data-final'.format(nome_parametro))
        ### --- Verifica exclusao m??tua de par??metros
        #### ---- Mais de um tipo de entrada (texto, arquivo ou lista)
        elif (args.text and args.filename_corpus and args.json_list):
            parser.error(
                'Nao e possivel passar mais de um o tipo de entrada (--texto, --lista, --arquivo)')
        elif (args.corpus_json is True and args.corpus_txt is True):
            parser.error(
                'Nao e possivel passar parametros -txt e -json simultaneamente')
        elif (args.text and (args.corpus_json is True or args.corpus_txt is True)):
            parser.error(
                'Nao e possivel passar parametros -txt e -json para uma entrada tipo --texto')
        elif (args.json_list and args.corpus_txt is True):
            parser.error(
                'Nao e possivel passar parametro -txt para uma entrada tipo --lista')
        ### --- Se tudo estiver ok, prossiga
        else:
            ### Carrega arquivos de configura????o na mem??ria
            __carrega_arquivos_de_configuracao()

            ### Define a t??cnica de combina????o padr??o
            ### Parametro tipo_combinacao ?? utilizado para testes e valida????o
            # tipo_combinacao = TIPO_COMBINACAO_LINEAR if args.tipo_combinacao is False else args.tipo_combinacao

            tipo_combinacao = TIPO_COMBINACAO_LINEAR

            explicacao = args.explicacao_metodo

            blacklist_extra = []
            ### Verifica se blacklist extra foi passada como parametro
            if args.filename_blacklist:
                with open(args.filename_blacklist, "r", encoding="utf-8") as file_input:
                    for termo in file_input:
                        blacklist_extra.append(termo)
            if args.blacklist_text:
                termos = args.blacklist_text.split(",")
                for termo in termos:
                    termo = termo.strip() ### remove espa??os que podem existir entre a v??rgula e o termo
                    blacklist_extra.append(termo)

            blacklist_extra = None if len(blacklist_extra) == 0 else blacklist_extra

            '''
            #DETERMINA TIPO DE ENTRADA
            '''
            #### texto ??nico
            if args.text:
                __imprime_resultado(text=args.text,blacklist_extra=blacklist_extra, explicacao=explicacao,
                                    tipo_combinacao=tipo_combinacao)

            #### lista de JSON
            elif args.json_list:
                import ast
                json_list = ast.literal_eval(args.json_list.replace("\n", ""))

                data_minima = __get_objeto_data(string_datetime=args.date_min, only_date=True)
                data_maxima = __get_objeto_data(string_datetime=args.date_max, only_date=True)

                for document in json_list:
                    __processa_documento_json(document=document, atributo_texto=args.attribute_name_text,
                                              atributo_data=args.attribute_name_date,
                                              data_minima=data_minima, data_maxima=data_maxima,
                                              blacklist_extra=blacklist_extra, explicacao=explicacao,
                                              tipo_combinacao=tipo_combinacao)

            #### corpus JSON ou TXT
            elif args.filename_corpus:
                data_minima = None
                data_maxima = None
                if args.corpus_txt is False:
                    data_minima = __get_objeto_data(string_datetime=args.date_min, only_date=True)
                    data_maxima = __get_objeto_data(string_datetime=args.date_max, only_date=True)

                with open(args.filename_corpus, "r", encoding="utf-8") as file_input:
                    for document in file_input:
                        #### --- Ou seja, Se corpus tipo JSON:
                        if args.corpus_json is True:
                            document = json.loads(document)
                            __processa_documento_json(document=document, atributo_texto=args.attribute_name_text,
                                                  atributo_data=args.attribute_name_date,
                                                  data_minima=data_minima, data_maxima=data_maxima,
                                                      blacklist_extra=blacklist_extra, explicacao=explicacao,
                                                      tipo_combinacao=tipo_combinacao)

                        #### --- Ou seja, Se corpus tipo TXT:
                        else:
                            __imprime_resultado(text=document, blacklist_extra=blacklist_extra, explicacao=explicacao,
                                                tipo_combinacao=tipo_combinacao)

            else:
                print("Nao foi possivel processar sua requisicao.")



    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,'\tData e Hora: ',datetime.now(),flush=True)

if __name__ == '__main__':
    main()