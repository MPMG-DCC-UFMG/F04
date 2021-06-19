#!/usr/bin/python

import sys
import os
from datetime import datetime

import re
import spacy
import json

import argparse

from collections import Counter
from datetime import datetime

nlp = spacy.load("pt_core_news_lg")


def __get_texto_sem_simbolos_especiais(text):
    text = text.replace('\n', " ").replace('#', "").replace('\"', "").replace('\'', "").replace(",", " ").replace(":",
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

def main():
    try:
        parser = argparse.ArgumentParser(description='Metodo para identificar propagandas eleitorais.')
        parser.add_argument('-t', '--texto', dest='text', type=str, default=False,
                            help='Texto para ser avaliado.')
        parser.add_argument('-c', '--corpus', dest='filename_corpus', type=str, default=False,
                            help='Caminho do arquivo que contem o corpus.')

        args = parser.parse_args()

        if args.text:
            text = __faz_limpeza_texto(text=args.text)

            score = __get_valence_score(text=text)

            score = round(score,3)

            print(score, flush=True)

        elif args.filename_corpus:
            with open(args.filename_corpus, "r", encoding="utf-8") as file_input:
                for text in file_input:
                    text = __faz_limpeza_texto(text=text)

                    score = __get_valence_score(text=text)

                    score = round(score, 3)

                    print(score, flush=True)

        else:
            print("Nao foi possivel processar sua requisicaco. Informe -t para processar um texto ou -c para processar um corpus.")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nError: ', e, '\tDetails: ', exc_type, fname, exc_tb.tb_lineno, '\tDatetime: ', datetime.now(),
              flush=True)


if __name__ == '__main__':
    # other_methods()
    main()