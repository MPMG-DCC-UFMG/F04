from src.com_info_extract import CommunityInformationExtractor
from src.data_extraction import DataExtraction

import pickle as pkl
import pandas as pd
import argparse
import os 
import sys
import json
import gc

def parser():
  """
  Declares the program's helper and argument reader.
  """
  
  parser = argparse.ArgumentParser(description="Programa responsável pela caracterização das comunidades \
  do backbone após a sua extração. É necessário fornecer um '.pkl' que contém os usuários das comunidades e \
  o dataframe original que foi utilizado para extrair o backbone. ")
  

  parser.add_argument('-input-file', '--input_file', help='Prefix name to save files', required=True)

  parser.add_argument("-pkl", "--community_pickle", help="Path to pickle.", required=True)
  
  parser.add_argument("-path_to_save", "--path_to_save", help="Path to save", required=True)

  parser.add_argument("-cfg", "--configuration_file", help="Path to the configuration file.", required=False)


  argument = parser.parse_args()

  return argument.input_file, argument.community_pickle, argument.path_to_save, argument.configuration_file



def main():
    path_to_csv, path_to_pkl, path_to_save, cfg_file = parser()
    
    print("Opening Configuration File")
    if cfg_file:
      f = open(cfg_file)
      cfg_file = json.load(f)['configuracoes_community_classification']


    deobj = DataExtraction()
    pkl = pd.read_pickle(path_to_pkl)
    twitter_df = pd.read_csv(path_to_csv)
    
    print("Extraindo mentions, keywords e hashtags do dataset!!")
    twitter_df['text'] = twitter_df['text'].astype(str)
    
    twitter_df['mentions'], twitter_df['keywords'], twitter_df['hashtags'] = deobj.extraction_facade(twitter_df['text'])

    com_obj = CommunityInformationExtractor(pkl)
    #Pega as comunidades com um número mínimo de membros

    csv_name =  path_to_csv.split('/')[-1].split('.')[0]

    print("Recuperando comunidades interessantes!")
    com_size = cfg_file['tamanho_da_comunidade'] if cfg_file and 'tamanho_da_comunidade' in cfg_file else 100

    community_list = com_obj.get_communities_with_more_than_k_pop(com_size)
    for community_number in community_list:
        data = com_obj.get_community_information(twitter_df, community_number, top_k=30)
    
        community_directory_name = f'community_{community_number}_{csv_name}'
    
        final_dir = os.path.join(path_to_save, community_directory_name)
        
        if not os.path.isdir(final_dir): os.mkdir(final_dir)
    
        com_obj.save_data(data, final_dir)
        print(f'Salvando comunidade de número {community_number}...')

if __name__ == "__main__":
    main()