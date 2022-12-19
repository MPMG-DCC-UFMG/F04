import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import sys
import argparse
import json

load_dotenv()

MONGO_USER = os.getenv('DB_USERNAME')
MONGO_PASS = os.getenv('DB_PASSWORD')
MONGO_HOST = os.getenv('DB_HOST')
MONGO_DBNAME = os.getenv('DB_NAME')
print(MONGO_USER, MONGO_PASS, MONGO_HOST)

mongo = MongoClient('mongodb://%s:%s@%s' %(MONGO_USER, MONGO_PASS, MONGO_HOST))
tweets = mongo[MONGO_DBNAME]['tweets']


STANDARD_OUTPUT_FOLDER = 'data/'
STANDARD_CONFIG_FILE = 'configuration/configuration.json'

def parser():
    """
    Declares the program's helper and argument reader.
    """

    parser = argparse.ArgumentParser(description="")

    parser.add_argument("-cfg", "--configuration_file", help="Path to the configuration file containing the dates", 
                        required=False)
    
    parser.add_argument("-pts", "--path_to_save", help="Path to save", required=False)

    argument = parser.parse_args()
    
    path_to_save = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), STANDARD_OUTPUT_FOLDER) if not argument.path_to_save else argument.path_to_save
    
    configuration_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), STANDARD_CONFIG_FILE) if not argument.configuration_file else argument.configuration_file

    print(path_to_save, configuration_file)

    return path_to_save, configuration_file

    


if __name__ == "__main__":
    path_to_save, configuration_file = parser()
    
    if configuration_file:
      f = open(configuration_file)
      configuration_file = json.load(f)['configuracoes_db_retrieval']
    
    date_min = datetime.strptime(configuration_file['data_inicio'], '%d/%m/%Y')
    
    date_max = datetime.strptime(configuration_file['data_fim'], '%d/%m/%Y')
    

    query = {"created_at": {
        "$gte": str(date_min),
        "$lt": str(date_max) 
    }, 
    # "retweeted_id": {"$exists": False}
    "retweet_id": {"$ne": None}}
    
    tweet_limit = configuration_file['limite_de_tweets']
    print("Recuperando Tweets na base!!!")
    cursor = tweets.find(query).limit(tweet_limit) if tweet_limit else tweets.find(query)

    print("Convertendo em Dataframe!!!")
    target_dataframe = pd.DataFrame(cursor)
    # convert query result to pandas dataframe
    
    #Treating Dataframe
    print("Tratando colunas!!!!")
    target_dataframe['author_id'] = target_dataframe.apply(lambda x: x['user']['id'], axis=1);
    target_dataframe.rename(columns={'retweet_id': 'referenced_tweets.retweeted.id'}, inplace=True);
    target_dataframe.drop('_id', axis=1, inplace=True);
    
    filename = f'Tweets_de_{date_min.date()}_ate_{date_max.date()}.csv'

    print("Salvando em CSV!!!!")
    target_dataframe.to_csv(f'{path_to_save}{filename}')
    
    print(target_dataframe)
