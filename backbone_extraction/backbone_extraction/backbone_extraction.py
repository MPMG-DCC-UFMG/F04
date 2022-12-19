from src.utils.data_extraction import DataExtraction
from src.utils.com_info_extract import CommunityInformationExtractor
from src.Backbone import Backbone
from src.utils.util_functions import *
from pathlib import Path

import pickle as pkl
import pandas as pd
import argparse
import os 
import sys
import json
import gc


GENERATED_FOLDER = 'output/backbone_files'

def parser():
  """
  Declares the program's helper and argument reader.
  """
  
  parser = argparse.ArgumentParser(description="Programa que calcula o backbone DFNB a partir de um grafo de co-retweets. \
    Para tal, é necessário fornecer um dataset de tweets que contenham ao menos quatro colunas: \
   'id, text, referenced_tweets.retweeted.id e author_id'. No modo padrão, o programa monta o grafo e extrai o backbone; O retorno do programa é um .edgelist contendo o backbone; \
    Por fim, é possível também fornecer somente o grafo para a extração do backbone. O dataset com tweets ou o grafo devem ser fornecidos. Caso ambos sejam fornecidos, o programa utilizará \
    apenas o grafo para calcular o backbone. ")
  

  parser.add_argument('-pfx', '--prefix', help='Prefix name to save files', required=False)

  parser.add_argument("-inf", "--input_file", help="Path to the dataset file.", required=True)
  
  parser.add_argument("-cfg", "--configuration_file", help="Path to the configuration file.", required=False)
  
  parser.add_argument('-save', "--path_to_save", help="Specify the path to save the backbone.", required=False)
   
  parser.add_argument('-graph', "--backbone_from_graph", help='Path to graph to extract backbone', required=False)

  argument = parser.parse_args()
  
  if not (argument.input_file) and not (argument.backbone_from_graph):
    raise Exception('Input file or graph must be provided;')

  file = argument.input_file; gph = argument.backbone_from_graph
  cfg_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), GENERATED_FOLDER)
  
  cfg_file = argument.configuration_file; path_to_save = cfg_file_path \
                                            if not argument.path_to_save else argument.path_to_save
  
  pfx = argument.prefix

  return file, cfg_file, path_to_save, gph, pfx



def get_backbone_from_edgelist(gph, cfg_file, path_to_save, pfx, sample_frac=0.2, 
                                                                  verbose=True, delete_intermediate=True):
    if cfg_file:
      percentil_nb = cfg_file['percentil_nb']
      percentil_threshold = cfg_file['percentil_threshold']
    else:
      percentil_nb = 95
      percentil_threshold = 95
      
    
    backbone = Backbone(percentil_threshold, percentil_nb);
    
    if verbose: print("Reading graph!")
    graph = pd.read_csv(gph)

    
    standard_proc_num = 10;
    if cfg_file and 'number_of_processes' in cfg_file: 
      standard_proc_num = int(cfg_file['numero_de_processos'])

    if verbose: print("Getting Threshold!!")
    thh_graph = backbone.get_threshold(graph)

    if verbose: print("Cleaning intermediate memory!")
    
    if delete_intermediate:
      del graph
      gc.collect()
    
    
    if verbose: print("Getting NB!!")
    final_backbone = backbone.calculate_nb(thh_graph, number_of_proc=standard_proc_num)

    if verbose: print("Saving Threshold+NB!!")
    final_backbone_path = f"{path_to_save}/{pfx}_Threshold_NB.edgelist"

    final_backbone.to_csv(final_backbone_path, index=False)

    if delete_intermediate:
      del final_backbone
      gc.collect()


    if verbose: print("Applying Louvain!")
    df, clusters = backbone.characterize_network_ig(final_backbone_path,
                                '_Threshold_NB', 
                                f'{pfx}', 
                                sample_frac, 
                                f'{backbone.percentile_threshold}-{backbone.percentile_nb}')

    if verbose: print("Saving Louvain!")

    df.to_csv(f"{path_to_save}/{pfx}_Networks_Characterization.csv", mode='a', header=False, index=None)
    pkl.dump(clusters, open(f"{path_to_save}/{pfx}_communities.pkl", "wb"), protocol=4)    


def clean_tweets(path_to_raw_tweets, cfg_file, path_to_save, pfx, sample_frac=0.2, verbose=True):


    if verbose: print("Reading raw_tweets!")

    raw_tweets = pd.read_csv(path_to_raw_tweets, 
    usecols=['id','text','referenced_tweets.retweeted.id', 'author_id'])
    
    raw_tweets['text'] = raw_tweets['text'].astype(str)

    de_obj = DataExtraction(); backbone = Backbone();

    if verbose: print("Processing Tweets!")
    processed_tweets = de_obj.clean_dataset(raw_tweets)


    if verbose: print("Getting and saving graph!!")
    edges = backbone.get_graph(processed_tweets) 

    final_path = f'{path_to_save}/{pfx}_graph.edgelist'

    backbone.save_graph(edges, path=final_path)

    if verbose: print("Liberating Memory!!!")
    free_object(raw_tweets, processed_tweets, backbone, edges)
    
    return final_path

def main():
    file, cfg_file, path_to_save, gph, pfx = parser()
    
    if cfg_file:
      f = open(cfg_file)
      cfg_file = json.load(f)["configuracoes_backbone_extractor"]

    pfx = file.split('/')[-1].split('.')[0]
    
    if not gph:
      gph = clean_tweets(file, cfg_file, path_to_save, pfx)
      gc.collect()
    
    get_backbone_from_edgelist(gph, cfg_file, path_to_save, pfx) 



if __name__ == "__main__":
    main()