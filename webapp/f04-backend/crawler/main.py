import pandas as pd
import numpy as np
import os
import sys
import json
import argparse


from crawler.Collector import Collector
from crawler.TwitterConn import TwitterConn

def parser():
  """
  Declares the program's helper and argument reader.
  """
  
  parser = argparse.ArgumentParser(description="")
  
  parser.add_argument("-af", "--authentication_file", help="Path to the authentication file.", required=False)
  
  parser.add_argument("-tc", "--tweets_csv", help="Path to CSV containing the tweets IDS.", required=False)

  parser.add_argument("-bp", "--saving_path", help="Path to save files", required=False)

  argument = parser.parse_args()
 
  #Um crime federal.
  file = argument.authentication_file if argument.authentication_file is not None else os.getcwd() + '/authentication/Bearer_tokens.json'

  k = argument.tweets_csv if argument.tweets_csv is not None else os.getcwd() + '/data/All_ids_current.csv'

  bp = argument.saving_path if argument.saving_path is not None else os.getcwd() + '/tweets/'
 

  return file, k, bp


def main():
	#path_to_authenticator = sys.argv[1]; path_to_tweets = sys.argv[2];

	path_to_authenticator, path_to_tweets, path_save_files = parser()

	with open(path_to_authenticator, 'r') as json_bearer:
		json_file = json.load(json_bearer)

	
	tweet_ids = pd.read_csv(path_to_tweets)
	
	#Criando os objetos de coleta
	twitter_con_obj = TwitterConn(json_file)
	
	collector_obj = Collector()

	# Verificando qual é o ID atual no .csv
	current_index = tweet_ids.loc[tweet_ids['current'] == 'X'].index[0]
	
	tweets_to_be_collected = tweet_ids.iloc[current_index:]['id'].tolist()
	
	try:
		collector_obj.tweet_lookup_and_save(tweets_to_be_collected, path_save_files, twitter_con_obj)
	
	except Exception as e:
		#Caso haja um erro durante a execução, salva a posição do último tweet capturado ( para retormar a coleta futuramente )
		#e encerra.
		last_id = int(e.args[1])

		tweet_ids.at[current_index, 'current'] = np.NAN

		last_collected = tweet_ids.loc[tweet_ids['id'] == last_id].index[0]

		tweet_ids.at[last_collected, 'current'] = 'X'

		tweet_ids.to_csv(path_to_tweets, index=False)

		print(f'Erro durante a execução: {e.args[0]}')


		
if __name__ == "__main__":
	main()



	
