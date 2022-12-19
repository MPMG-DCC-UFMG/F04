import pandas as pd
import numpy as np
import time
import itertools
import networkx as nx
import igraph as ig
import csv
import pickle as pkl
import random
import gc

from multiprocessing import Pool
from tqdm import trange, tqdm

class Backbone():
    
    def __init__(self, percentil_threshold=95, percentile_nb=95):
        self.percentile_threshold = percentil_threshold
        
        self.percentile_nb = percentile_nb
        
    
    def get_graph(self, df):
        
        dict_edges = {}
        set_tweets = set(df['referenced_tweets.retweeted.id'])
        
        for tweet in set_tweets:
            df_temp = df[df['referenced_tweets.retweeted.id'] == tweet]
            set_users = sorted(set(df_temp['author_id']))

            for edge in itertools.combinations(set_users, 2):
                if edge not in dict_edges:
                    dict_edges[edge] = 0
                dict_edges[edge] += 1
        
        return dict_edges

    def save_graph(self, dict_edges, path=None):
        try:
            with open(path, 'w+') as f:
                f.write("src,trg,nij\n")    
                for edge, weight in dict_edges.items():
                    f.write(str(edge[0])+","+str(edge[1])+','+str(weight)+"\n")    
        except Exception as e:
            raise Exception(f'{e}.\nError during the saving process of graph_edges. Terminating;\n')

    
    def get_dfnb(self, graph, proc_num=15, chk=100):
        df_graph = self.disparity_filter(graph)
        
        df = self.calculate_nb(df_graph, proc_num, chk)
        
        return df
    

    def get_threshold_nb(self, graph, proc_num=15, chk=100, clean_intermediate=True):
        thh_graph = self.get_threshold(graph)
        
        if clean_intermediate:
            del graph
            gc.collect()

        df = self.calculate_nb(thh_graph, proc_num, chk)
        
        return df


    def get_threshold(self, dict_edges):
        dict_edges = dict_edges[dict_edges['nij'] >= np.percentile(dict_edges['nij'], 
                                                        self.percentile_threshold)]
        return dict_edges

    def calculate_nb(self, df, number_of_proc=15, chunks=100, clean_intermediate=True):
        global G

        G = nx.from_pandas_edgelist(df, source='src', target='trg', edge_attr='nij')
        
        
        if clean_intermediate:
            del df
            gc.collect()

        # Use a global variable to allow all process to see the graph; 
        
        proc = Pool(number_of_proc)
        for u, v, nb in tqdm(proc.imap_unordered(neighborhood_overlap_global, list(G.edges()), chunksize=chunks),
                            position=0, leave=False, total=int(G.number_of_edges())):  
            G[u][v]['nb'] = nb  
            
        proc.close()
        
        proc.join()
        
        nb = nx.get_edge_attributes(G, "nb")
        
        threshold = np.percentile(list(nb.values()), self.percentile_nb)
        
        edges_to_remove = []
        
        count = 0
        
        for u, v , a in G.edges(data=True):
            if a['nb'] < threshold:
                edges_to_remove.append((u, v))
        
        G.remove_edges_from(edges_to_remove)
        

        new_df = nx.to_pandas_edgelist(G)
        
        if clean_intermediate:
            del G
            gc.collect()

        new_df.columns = ['src','trg','nij','nb']

        return new_df

    def read(self, filename, column_of_interest, triangular_input = True, consider_self_loops = False, 
            undirected = True, drop_zeroes = False):
        """Reads a field separated input file into the internal backboning format (a P
        andas Dataframe).
        The input file should have three or more columns (default separator: tab).

        The input file must have a one line header with the column names.

        There must be two columns called 'src' and 'trg', indicating the origin and destination of the interaction.
        All other columns must contain integer or floats, indicating the edge weight.
        
        In case of undirected network, the edges have to be present in both directions with the same weights, or set triangular_input to True.
        
        Args:
        
        filename (str): The path to the file containing the edges.
        column_of_interest (str): The column name identifying the weight that will be used for the backboning.
        
        KWArgs:
        
        triangular_input (bool): Is the network undirected and are the edges present only in one direction? default: False
        
        consider_self_loops (bool): Do you want to consider self loops when calculating the backbone? default: True
        
        undirected (bool): Is the network undirected? default: False
        
        drop_zeroes (bool): Do you want to keep zero weighted connections in the network? Important: it affects methods based on degree, like disparity_filter. default: False
        
        sep (char): The field separator of the inout file. default: tab
        
        Returns:

        The parsed network data, the number of nodes in the network and the number of edges.
        """

        table = pd.read_csv(filename)
        table = table[["src", "trg", column_of_interest]]
        table.rename(columns = {column_of_interest: "nij"}, inplace = True)
        if drop_zeroes:
            table = table[table["nij"] > 0]
        if not consider_self_loops:
            table = table[table["src"] != table["trg"]]
        if triangular_input:
            table2 = table.copy()
            table2["new_src"] = table["trg"]
            table2["new_trg"] = table["src"]
            table2.drop("src", 1, inplace = True)
            table2.drop("trg", 1, inplace = True)
            table2 = table2.rename(columns = {"new_src": "src", "new_trg": "trg"})
            table = pd.concat([table, table2], axis = 0)
            table = table.drop_duplicates(subset = ["src", "trg"])
        original_nodes = len(set(table["src"]) | set(table["trg"]))
        original_edges = table.shape[0]
        if undirected:
            return table, original_nodes, original_edges / 2
        else:
            return table, original_nodes, original_edges

    def disparity_filter(self, table, undirected = True):
        #sys.stderr.write("Calculating DF score...\n")
        #table = table.copy()
        table_sum = table.groupby(table["src"]).sum().reset_index()
        table_deg = table.groupby(table["src"]).count()["trg"].reset_index()
        table = table.merge(table_sum, on = "src", how = "left", suffixes = ("", "_sum"))
        table = table.merge(table_deg, on = "src", how = "left", suffixes = ("", "_count"))
        table["score"] = 1.0 - ((1.0 - (table["nij"] / table["nij_sum"])) ** (table["trg_count"] - 1))
    # table["variance"] = (table["trg_count"] ** 2) * (((20 + (4.0 * table["trg_count"])) / ((table["trg_count"] + 1.0) * (table["trg_count"] + 2) * (table["trg_count"] + 3))) - ((4.0) / ((table["trg_count"] + 1.0) ** 2)))
        # if not return_self_loops:
        #     table = table[table["src"] != table["trg"]]
        if undirected:
            table["edge"] = table.apply(lambda x: "%s-%s" % (min(x["src"], x["trg"]), max(x["src"], x["trg"])), axis = 1)
            table_maxscore = table.groupby(by = "edge")["score"].max().reset_index()
        #  table_minvar = table.groupby(by = "edge")["variance"].min().reset_index()
            table = table.merge(table_maxscore, on = "edge", suffixes = ("_min", ""))
        #  table = table.merge(table_minvar, on = "edge", suffixes = ("_max", ""))
            table = table.drop_duplicates(subset = ["edge"])
            table = table.drop("edge", 1)
            table = table.drop("score_min", 1)
        #   table = table.drop("variance_max", 1)
        return table[["src", "trg", "nij", "score"]]


    def characterize_network_ig(self, file_name, type_network, 
    snap, sample_frac, parameter):
        #Gix = ig.Graph.DataFrame(df[['src','trg']], directed=False)
        
        file = open(file_name)
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader)
        tupleMapping = []
        for line in csv_reader:
            source = int(line[0])
            target = int(line[1])
            l = [source, target]
            tupleMapping.append(tuple(l))
        Gix = ig.Graph.TupleList(tupleMapping)
        
        graph_metrics = dict()
        list_results = []
        graph_metrics["n_nodes"] = Gix.vcount()
        graph_metrics["n_edges"] = Gix.ecount()
        graph_metrics["avg_degree"] = round(ig.mean(Gix.degree()),2)
        graph_metrics["density"] = round(Gix.density(),4)
        graph_metrics["n_connected_components"] = len(list(Gix.components()))

        
        clusters = Gix.community_multilevel(return_levels=False)
        graph_metrics["modularity"] = round(Gix.modularity(clusters),4)
        clusters = list(clusters)
        graph_metrics["n_comm"] = len(clusters)
        # Converter clusters para o index ao invés de ID
        flat_list = [item for sublist in clusters for item in sublist]
        dict_index2node = Gix.vs.select(flat_list)
        dict_index2node = dict(zip(flat_list, dict_index2node['name']))
        clusters={i: member for i, member in enumerate(clusters)}
        clusters_updated_name = dict()
        for comm, list_members in clusters.items():
            for member in list_members:
                clusters_updated_name[dict_index2node[member]] = comm
        clusters = clusters_updated_name
        # del clusters_updated_name
        # pkl.dump(clusters, open(Path_Communities, "wb"), protocol=4)    
        #Computing the clustering coefficient from a sample
        k = int(graph_metrics['n_nodes']*sample_frac)
        node_sample_list = list(random.sample(list(range(0, graph_metrics['n_nodes'])),k))
        node_sample_list = Gix.vs.select(node_sample_list)
        graph_metrics["avg_clustering"] = round(np.nanmean(Gix.transitivity_local_undirected(vertices=node_sample_list, mode='Nan')),4)
        #del subgraph
        
        network = "MPMG"    
       
        list_results.append((network, type_network, snap, graph_metrics['n_nodes'], graph_metrics['n_edges'], 
                        graph_metrics['avg_degree'], graph_metrics['density'], graph_metrics['avg_clustering'],
                            graph_metrics['n_connected_components'], graph_metrics['n_comm'], graph_metrics['modularity'], parameter))
        
        df = pd.DataFrame(list_results, columns=['Network', 'Type', 
                                            'Snapshot', '# Nodes', '# Edges', 'Avg. Degree',
                                            'Density', 'Avg. Clustering', '# Components',
                                            '# Communities', 'Modularity', "Parameter"])

        
        return df, clusters



# Global reference to graph, to allow all created process to see it; 
G = None

def neighborhood_overlap_global(edge):
    
    u = edge[0]; v = edge[1];
    
    n_common_nbrs = len(set(nx.common_neighbors(G, u, v)))
    
    if n_common_nbrs == 0:
        return u,v,0 
    
    else:
        n_join_nbrs = G.degree(u) + G.degree(v) - n_common_nbrs - 2
        return u,v,n_common_nbrs/n_join_nbrs