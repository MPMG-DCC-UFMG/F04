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

nlp = spacy.load("pt_core_news_lg")

def __get_texto_sem_simbolos_especiais(text):
    text = text.replace('\n', " ").replace('#', "").replace('\"', "").replace('"', "").replace('\'', "").replace("'", "").replace(",", " ").replace(":",
                                                                                                                  "").replace(
        ".", "").replace(";", "").replace("!", "").replace("@", "").replace("$", "").replace("%", "").replace("&",
                                                                                                              "").replace(
        "?", "").replace("*", "").replace("-", " ").replace("(", "").replace(")", "").replace("+", "").lower()

    my_val = str(text).rstrip("\n").rstrip("\t").rstrip("\r")
    my_val = str(my_val).replace('\r', " ").replace('\n', " ").replace('\t', " ")
    text = my_val.strip()

    ### remove emojis
    text = ' '.join(re.split("[^a-z|0-9|á|é|í|ó|ú|â|ê|î|ô|û|ã|õ|à|ç|/|ü]+", text))

    return text


def __get_texto_reforcado(text):
    ### Substitui endereços de URLs pela palavra link
    text = 'link'.join(re.split("http\S+", text))

    ### Substitui palavras por palavras de reforço da lista
    palavras_reforco = []
    with open("palavras_reforco.json", "r", encoding="utf-8") as file_input:
        for document in file_input:
            document = json.loads(document)
            palavras_reforco.append((document["palavra_original"], document["nova_palavra"]))

    for palavra_info in palavras_reforco:
        text = (" " + text + " ").replace(" " + palavra_info[0] + " ", " " + palavra_info[1] + " ")
        text = text[1:len(text) - 1]

    return text


def __get_texto_lematizado(text):
    doc = nlp(text)
    text = ' '.join([token.lemma_ for token in doc])

    return text


def __faz_limpeza_texto(text):
    text = __get_texto_sem_simbolos_especiais(text=text)
    text = __get_texto_reforcado(text=text)
    text = __get_texto_lematizado(text=text)

    return text

def __get_normalized_value(value, max_value, min_value):
    normalized = (value - min_value) / (max_value - min_value)

    return normalized


def __get_valence_score(text):
    string_list = text.split(" ")

    termos = {}
    with open("pesos_palavras.json", "r", encoding="utf-8") as file_input:
        for document in file_input:
            document = json.loads(document)
            termos[document["palavra"]] = document["peso"]

    ### Filtra somente as palavras que estão nos termos considerados
    string_list = list(filter(lambda x: x in termos, string_list))

    score = 0
    for palavra in string_list:
        score += termos[palavra]

    if len(string_list) > 0:
        score = score/len(string_list)

    ### O score maximo acontece quando todas as palavras do texto sao termos com score 1
    score = __get_normalized_value(value=score, max_value=1, min_value=0) if score > 0 else 0

    return score

def __verifica_presenca_em_blacklist(text, blacklist_extra=None):
    text = __faz_limpeza_texto(text=text)

    with open("blacklist.txt", "r", encoding="utf-8") as file_input:
        for termo in file_input:
            termo = __faz_limpeza_texto(text=termo)

            if termo in text:
                return True

    if blacklist_extra is not None:
        for termo in blacklist_extra:
            termo = __faz_limpeza_texto(text=termo)

            if termo in text:
                return True

    return False

def __imprime_resultado(text, blacklist_extra):
    if text is not None and len(text) > 0:
        #### Verifica se texto contem termos da blacklist
        result = __verifica_presenca_em_blacklist(text=text, blacklist_extra=blacklist_extra)
        if result is True:
            score = 0
        else:
            text = __faz_limpeza_texto(text=text)

            score = __get_valence_score(text=text)

            score = round(score, 3)

        print(score, flush=True)
    else:
        print("ERRO: texto nulo ou vazio.", flush=True)


def __get_objeto_data(string_datetime, only_date=False):
    a_datetime = None
    string_datetime = string_datetime.replace("\"", "")
    string_datetime = string_datetime.replace("'", "")

    if only_date is True:
        datetime_pattern = '%Y-%m-%d'
        try:
            a_datetime = datetime.strptime(string_datetime, datetime_pattern)
            return a_datetime.date()
        except Exception as e:
            print("ERRO ao formatar string como DATA:", string_datetime, "DETALHES:", e, flush=True)
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

            return (a_datetime)

def __processa_documento_json(document, atributo_texto, atributo_data, data_minima, data_maxima, blacklist_extra):
    if atributo_texto in document and atributo_data in document:
        data_documento = __get_objeto_data(string_datetime=document[atributo_data])

        if data_documento >= data_minima and data_documento <= data_maxima:
            __imprime_resultado(text=document[atributo_texto], blacklist_extra=blacklist_extra)
    else:
        print("ERRO: documento nao possui atributo de texto ou atributo de data.")


def main():
    try:
        parser = argparse.ArgumentParser(description='Metodo para identificar propagandas eleitorais.')

        '''
        ###############
        ARGUMENTOS OBRIGATÓRIOS
        ###############
        '''
        #### texto único --- OU
        parser.add_argument('--texto', '-t',dest='text', type=str, default=False,
                            help='Texto para ser avaliado.')
        #### lista de JSON --- OU
        parser.add_argument('--lista', '-l',  dest='json_list', type=str, default=False,
                            help='Lista no formato JSON com os documentos.')
        #### corpus JSON ou TXT (por padrão, o corpus é JSON)
        parser.add_argument('--corpus', '-c', dest='filename_corpus', type=str, default=False,
                            help='Caminho do arquivo que contem o corpus.')
        #### --- Se corpus tipo JSON:
        # parser.add_argument('-json', dest='corpus_json', type=str, default=False,
        #                     help='Declara que tipo do corpus como JSON')
        parser.add_argument('--atributo-texto', '-at', dest='attribute_name_text', type=str, default=False,
                            help='Nome do atributo no JSON que contem o texto.')
        parser.add_argument('--atributo-data', '-ad', dest='attribute_name_date', type=str, default=False,
                            help='Nome do atributo no JSON que contem o texto.')
        parser.add_argument('--data-minima', '-dmin',  dest='date_min', type=str, default=False,
                            help='Data minima para a filtragem (limite inferior).')
        parser.add_argument('--data-maxima', '-dmax', dest='date_max', type=str, default=False,
                            help='Data maxima para a filtragem (limite superior).')

        #### --- Se corpus tipo TXT:
        parser.add_argument('-txt',action='store_true', dest='corpus_txt', default=False,
                            help='Declara que tipo do corpus como TXT')

        '''
        ###############
        ARGUMENTOS OPCIONAIS
        ###############
        '''
        parser.add_argument('--blacklist-arquivo', '-ba', dest='filename_blacklist', type=str, default=False,
                            help='Caminho do arquivo que contem termos para acrescentar na blacklist.')
        parser.add_argument('--blacklist-texto', '-bt', dest='blacklist_text', type=str, default=False,
                            help='Texto que contem termos para acrescentar na blacklist.')

        '''
        ###############
        PROCESSA ARGUMENTOS DE PROGRAMA E VERIFICA ERROS
        ###############
        '''
        args = parser.parse_args()

        if (args.filename_corpus or args.json_list) and (args.attribute_name_text is None or args.attribute_name_date is None or
                                             args.date_min is None or args.date_max is None):
            nome_argumento = "--corpus" if args.filename_corpus else "--lista"
            parser.error('O argumento {} exige que seja informado --atributo-texto, --atributo-data, --data-minima e --data-maxima'.format(nome_argumento))
        else:
            ### Verifica se blacklist extra foi passada como parametro
            if args.filename_blacklist:
                blacklist_extra = []
                with open(args.filename_blacklist, "r", encoding="utf-8") as file_input:
                    for termo in file_input:
                        blacklist_extra.append(termo)
            elif args.blacklist_text:
                blacklist_extra = []
                termos = args.blacklist_text.split(",")
                for termo in termos:
                    blacklist_extra.append(termo)
            else:
                blacklist_extra = None

            '''
            DETERMINA TIPO DE ENTRADA
            '''
            #### texto único
            if args.text:
                __imprime_resultado(text=args.text,blacklist_extra=blacklist_extra)

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
                                              blacklist_extra=blacklist_extra)

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
                        if args.corpus_txt is False:
                            document = json.loads(document)
                            __processa_documento_json(document=document, atributo_texto=args.attribute_name_text,
                                                  atributo_data=args.attribute_name_date,
                                                  data_minima=data_minima, data_maxima=data_maxima,
                                                      blacklist_extra=blacklist_extra)

                        #### --- Ou seja, Se corpus tipo TXT:
                        else:
                            __imprime_resultado(text=document, blacklist_extra=blacklist_extra)

            else:
                print("Nao foi possivel processar sua requisicaco.")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nError: ', e, '\tDetails: ', exc_type, fname, exc_tb.tb_lineno, '\tDatetime: ', datetime.now(),
              flush=True)


if __name__ == '__main__':
    main()