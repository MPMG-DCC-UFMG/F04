import pandas as pd
import numpy as np
import matplotlib as plt
import collections

from wordcloud import WordCloud, STOPWORDS
from nltk.tokenize import WordPunctTokenizer, word_tokenize
from bs4 import BeautifulSoup

from itertools import islice
from functools import reduce

class CommunityInformationExtractor():
    
    def __init__(self, pkl):
        """
            Arguments
            ----------
            pkl: Arquivo '.pkl' que contém informações sobre as comunidades e seus respectivos usuários.
        
        """
        self.community_dict = self.__get_community_dict(pkl)
        
    
    def get_largest_communities_index(self, quantity):
        comm = dict(sorted(self.community_dict.items(), key = lambda x: len(x[1]), reverse=True)[:quantity]).keys()
        return comm
    
    def get_communities_with_more_than_k_pop(self, quantity):
        keys = list({k for k,v in self.community_dict.items() if len(v) >= quantity})
        keys = list(sorted(keys, key=lambda x: len(self.community_dict[x]), reverse=True))
        return keys
    
    def get_community_information(self, df, community_number, top_k=30, generate_word_cloud=True):
        

        filtered_users = df[df['author_id'].isin(self.community_dict[community_number])]
            
        data = self.get_top_hashtags_keywords_mentions(
            list(filtered_users[filtered_users['hashtags'].isnull() == False]['hashtags']),
            list(filtered_users[filtered_users['keywords'].isnull() == False]['keywords']),            
            list(filtered_users[filtered_users['hashtags'].isnull() == False]['hashtags']),
            top_k)
    
        data['general_info'] = self.__get_general_information(filtered_users, community_number)

        data['wordcloud'] = None
        
        if generate_word_cloud:
            data['wordcloud'] = self.generate_word_cloud(filtered_users['text'])
            
        return data
    
    
    def get_time_of_authors_life(self, df, author_list):
        
        author_dict = {}
        for author_id in author_list:

            author_tweets = df[df['author_id'] == author_id]
            author_creation_date = pd.to_datetime(author_tweets.iloc[0]['author.created_at'])
            times = author_tweets.apply(lambda x: pd.to_datetime(x['created_at']) - author_creation_date, axis=1)
            account_life = min(times)
            author_dict[author_id] = account_life
        
        return author_dict
    
    
    def similarity_of_content_between_members(self, df, author_list):
        size = len(author_list)
        sim_matrix = np.zeros((size, size))
        
        
        for i in range(size):
            author_target_tweets = set(df[df['author_id'] == author_list[i]]['text'].unique())
            for j in range(size):
                if i == j:
                    continue
                author_pair = set(df[df['author_id'] == author_list[j]]['text'].unique())

                intersection = author_target_tweets.intersection(author_pair)
                
                union = author_pair.union(author_target_tweets)

                sim_matrix[i][j] = len(intersection)/len(union)
            
        mean_val = np.mean(sim_matrix); std_deviation = np.std(sim_matrix)
        return mean_val, std_deviation
                
    
    def get_summarized_community_information(self, df, community_list, backbone=""):
        dataframe = pd.DataFrame()
        first_iteration = True
        for community_number in community_list:
            data = {}
            
            filtered_users = df[df['author_id'].isin(self.community_dict[community_number])]

            data['community'] = community_number

            data['backbone'] = backbone

            author_id_list = filtered_users['author_id'].unique()

            data['number_of_users'] = len(author_id_list)

            data['number_of_verified_users'] = len(filtered_users[filtered_users['author.verified'] == True]['author_id'].unique())

            data['number_of_retweets_total'] = len(filtered_users)

            data['number_of_distinct_tweets'] = len(filtered_users['text'].unique())

            data['mean_retweet_number_by_user'] = len(filtered_users['author_id'])/len(filtered_users['author_id'].unique())

            rt_times = self.get_community_times(df, [community_number])

            data['sequencial_rt_median'] = np.median(rt_times[community_number])

            data['sequencial_rt_mean'] = sum(rt_times[community_number])/len(rt_times[community_number])

            data['sequencial_rt_mean_normalized'] = data['sequencial_rt_mean']/data['number_of_users']

            acc_life_times = self.get_time_of_authors_life(filtered_users, author_id_list)

            data['account_life_time_mean'] = pd.Series(acc_life_times.values()).mean()

    #         mean, std_dev = self.similarity_of_content_between_members(filtered_users, author_id_list)

    #         data['content_similarity_jaccard_mean'] = mean

    #         data['content_similarity_std_dev'] = std_dev

            data = pd.DataFrame.from_dict(data,orient='index').T
            dataframe = dataframe.append(data)
        
        
        return dataframe
        

    def __get_general_information(self, df, community_number):
        information = {}
        information['numero_de_usuarios_na_comunidade'] = len(self.community_dict[community_number])
        information['numero_de_tuites_na_comunidade'] = len(df)
        return information

    def get_top_hashtags_keywords_mentions(self, hashtags, keywords, mentions, top_k):

        data = {}

        top_hashtags = self.get_sorted_information(hashtags, top_k)
        
        top_keywords = self.get_sorted_information(keywords, top_k)   
        
        top_mentions = self.get_sorted_information(mentions, top_k)
        
        data['hashtags'] = top_hashtags; data['keywords'] = top_keywords; data['mentions'] = top_mentions;
        
        return data
        
    
    def get_sorted_information(self, information, top_k=0):    
        data = {}
        
        if len(information) != 0:
            data = reduce(add, information)
            data = collections.Counter(data)
            
            data = dict(sorted(data.items(), key = lambda x: x[1], reverse = True))
            
            if top_k and len(data) > top_k:
                data = dict(islice(data.items(), top_k))
            
        return data
    
    
    def generate_word_cloud(self, tweets):
        tweets = tweets.apply(self.clean_tweets)
        
        wordcloud = pd.Series(tweets).str.cat(sep=' ')
        
        token = WordPunctTokenizer()
        wordcloud = WordCloud(width=1600, stopwords=stopwords, height=800,
                            max_font_size=200, max_words=100, collocations=True, 
                            background_color='black').generate(wordcloud)
  
        return wordcloud
        
        

    def clean_tweets(self, tweet):
        regex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)

        tweet = re.sub(regex_pattern,'',tweet)

        #URL's
        pattern = re.compile(r'(https?://)?(www\.)?(\w+\.)?(\w+)(\.\w+)(/.+)?')
        tweet = re.sub(regex_pattern,'',tweet)
        tweet = re.sub(r'[^\w\s]','',tweet, re.UNICODE)
        tweet = BeautifulSoup(tweet, 'lxml')
        tweet = tweet.get_text()
        tweet = tweet.lower()
        words = word_tokenize(tweet)
        words = ' '.join([x for x in words if len(x) > 2])
        return words
    
    def __get_community_dict(self, pkl):
        inverted_dict = {}
        for key, value in pkl.items():
            
            if value not in inverted_dict: inverted_dict[value] = []
            inverted_dict[value].append(key)
        
        return inverted_dict
    
    
    def save_data(self, data, path):
  
        for key in [k for k in data.keys() if k != 'wordcloud']:
            with open(f'{path}/{key}.txt', 'w+') as file:
                file.write(json.dumps(data[key], ensure_ascii=False))
            
        if data['wordcloud'] != None:
            plt.figure(figsize=(40,30))
            plt.imshow(data['wordcloud'], interpolation="bilinear")
            plt.axis("off")
            plt.savefig(f"{path}/wordcloud.pdf")

    
    def show_wordcloud(self, wc):
        plt.figure(figsize=(40,30))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.show()
        
    def get_community_times(self, twitter_df, community_list):
        general_list = {}
        second_list = []

        for comm in community_list:
            filtered_users = twitter_df[twitter_df['author_id'].isin(self.community_dict[comm])]
            for item in filtered_users['referenced_tweets.retweeted.id'].unique():
                people_who_retweeted_a_unique_tweet = filtered_users[filtered_users['referenced_tweets.retweeted.id'] == item]
                ordered_times = list(sorted(pd.to_datetime(people_who_retweeted_a_unique_tweet['created_at'])))
                #Getting time difference, in seconds, between all consecutive elements of the list.
                for time in range(len(ordered_times)-1):
                    time_difference = (ordered_times[time+1] - ordered_times[time]).total_seconds()
                    second_list.append(time_difference)
            #second_list = [x for x in second_list if x <= 2000]
            
            general_list[comm] = second_list
            second_list = []
            
        return general_list