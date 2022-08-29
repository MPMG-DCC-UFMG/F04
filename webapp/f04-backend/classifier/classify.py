
from utils.helpers import gen_data
import gensim
from sklearn.feature_extraction.text import HashingVectorizer
import joblib
import pandas as pd
from utils.text_processor import TextProcessor
from utils.political_classification import PoliticalClassification
import argparse
import os
import numpy as np
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
EMBEDDING_DIM = 300
MAX_SEQUENCE_LENGTH = 240

from dotenv import load_dotenv
load_dotenv(dotenv_path= "/code/.env")
from pymongo import MongoClient

MONGO_USER = os.getenv('DB_USERNAME')
MONGO_PASS = os.getenv('DB_PASSWORD')
MONGO_HOST = os.getenv('DB_HOST')
MONGO_DBNAME = os.getenv('DB_NAME')

mongo = MongoClient('mongodb://%s:%s@%s' %(MONGO_USER, MONGO_PASS, MONGO_HOST))
tweets = mongo[MONGO_DBNAME]['tweets']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Ferramenta de Classificação de Textos')

    MODEL = os.getenv('MODEL')
    MODEL_FILE = os.getenv('MODEL_FILE')  # Arquivo h5 para CNN e SKL para outros modelos
    NPY_FILE = os.getenv('NPY_FILE')  # Necessário apenas para a CNN ou Modelos de Deep Learning
    WORD2VEC_FILE = os.getenv('WORD2VEC_FILE')

    try:
        if MODEL in ['cnn', 'rnn', 'lstm', 'han'] and NPY_FILE is None:
            raise Exception(
                'Para o modelo CNN é obrigatório informar o caminho para o MODELO (Arquivo H5) e o arquivo do Vocabulário (NPY) ')
        if not os.path.isfile(MODEL_FILE):
            raise Exception('O arquivo [%s] não existe!' % (MODEL_FILE))
        if MODEL == 'cnn' and not os.path.isfile(NPY_FILE):
            raise Exception('O arquivo [%s] não existe!' % (NPY_FILE))

        if MODEL in ['svm', 'rforest', 'lregression', 'gboost'] and (not WORD2VEC_FILE or not os.path.isfile(WORD2VEC_FILE)):
            raise Exception(
                'O arquivo WORD2VEC [%s] não existe! Ele é obrigatório para os modelos SVM, Random Forest, Logistic Regression e Gradient Boosting' % (WORD2VEC_FILE))

    except Exception as error:
        print(WORD2VEC_FILE)
        print('ERRO: %s' % (error))
        exit(0)

  
    tp = TextProcessor()
    #texts_df = pd.read_csv(INPUT_FILE)
    #texts = list(texts_df['text'])
    #texts = tp.text_process(texts, text_only=True)
    #X = list(texts_df['text'])
    Y = []
    query = {}
    query['score'] = { '$exists': False }
    #query['retweet_id'] = { '$exists': False }
    cursor = tweets.find(query).limit(1000)

    if MODEL in ['cnn', 'rnn', 'lstm', 'han']:
        pc = PoliticalClassification(MODEL_FILE, NPY_FILE, MAX_SEQUENCE_LENGTH)

        for tweet in cursor:

            text = tweet['text']

            text = tp.text_process([text], text_only=False)[0]

            if MODEL == 'han':
                Y.append(pc.is_political_prob_han(' '.join(text)))
            else:
                probability = pc.is_political_prob(' '.join(text))
                print ("#" * 10)
                print(text)
                print("(%s)" % (probability))
                print ("#" * 10)
                print()
            tweets.find_one_and_update({'_id': tweet['_id']}, {
                "$set": {"score": float(probability)}})
                
        exit(0)

    elif MODEL == 'naive':
        model = joblib.load(MODEL_FILE)

        vectorizer = HashingVectorizer(
            alternate_sign=False,
            n_features=500000,
            ngram_range=(1, 3)
        )
        texts = [' '.join(txt) for txt in texts]
        texts = vectorizer.transform(texts)
        for text in texts:
            prob = model.predict_proba(text)
            Y.append(prob[0][1])

        pass


   
