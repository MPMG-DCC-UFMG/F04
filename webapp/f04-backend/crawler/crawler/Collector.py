import json
from twarc.expansions import ensure_flattened
import os
from pymongo import MongoClient
PLACE_FIELDS = 'country,name,place_type'

EXPANSIONS = 'attachments.media_keys,referenced_tweets.id.author_id,geo.place_id'

TWEET_FIELDS = 'attachments,author_id,created_at,entities,geo,id,in_reply_to_user_id,public_metrics,text,referenced_tweets'

USER_FIELDS = 'created_at,description,id,name,username,verified,location,url,profile_image_url'


MONGO_USER = os.getenv('DB_USERNAME')
MONGO_PASS = os.getenv('DB_PASSWORD')
MONGO_HOST = os.getenv('DB_HOST')

mongo = MongoClient('mongodb://%s:%s@%s' %
                    (MONGO_USER, MONGO_PASS, MONGO_HOST))

print('mongodb://%s:%s@%s' % (MONGO_USER, MONGO_PASS, MONGO_HOST))

class Collector:								
	
	def write_on_folder(self, msg, id_post, base_path):
			"""
			Salva texto do post na pasta adequada. 
			"""
			name = base_path + str(id_post) + '.json'

			with open(name, 'w') as f:
					f.write(msg)

	def dumps(self, sts):
			"""
			Retorna a string em json dos atributos de interesse num tweet.
			As duas coletas usam essa função para filtragem.
			Parametros
			----------
			sts : Status
					Um objeto de tweet.
			Retorna
			-------
			str
					Texto json do tweet.
			"""
	#Cria todos os atributos.
			status = {}
			status['id'] = sts['id']
			status['text'] = sts['text']
			status['created_at'] = str(sts['created_at'])
			status['quote_count'] = sts['public_metrics']['quote_count']
			status['reply_count'] = sts['public_metrics']['reply_count']
			status['retweet_count'] = sts['public_metrics']['retweet_count']
			status['favorite_count'] = sts['public_metrics']['like_count']
			status['location'] = sts['geo']['full_name'] \
					if 'geo' in sts and 'full_name' in sts['geo'] else None
			status['retweet_id'] = None
			status['retweeted_user_id'] = None
			status['in_reply_to_status_id'] = None
			status['in_reply_to_user_id'] = None
			status['user'] = sts['author']
			#Verifica se existe algum tweet que interage com o tweet capturado. Se houver, pega o tipo o ID do tweet, e o ID do autor.
			if 'referenced_tweets' in sts:
					tweet_interaction = sts['referenced_tweets'][0]['type']
					id_tweet_interacao = sts['referenced_tweets'][0]['id']

					#Considerando que em alguns poucos casos a API do twitter não retorna o author_id.
					try:
							referenced_author_id = sts['referenced_tweets'][0]['author_id']
					except:
							pass

					if tweet_interaction == 'retweeted':

							try:
									status['retweeted_user_id'] = referenced_author_id 
							except:
									pass

							status['retweet_id'] = id_tweet_interacao

					elif tweet_interaction == 'replied_to':
							status['in_reply_to_status_id'] = id_tweet_interacao
							status['in_reply_to_user_id'] = sts['in_reply_to_user_id'] \
									if 'in_reply_to_user_id' in sts else None   


			return json.dumps(status, ensure_ascii=False)
    
    
	def tweet_lookup_and_save(self, tweet_list, base_path, twitter_obj, verbose=True):		
		"""
		Recebe uma lista de tuítes para realizar o retrieval. Para cada tweet recuperado, é realizado
		o salvamento de um '.json' que representa o tweet no base_path. O nome do arquivo é correspondente
		ao tweet_id. 
		"""
		
		endpoint_obj = twitter_obj.get_next_api()

		response = endpoint_obj.tweet_lookup(tweet_list, EXPANSIONS, TWEET_FIELDS, 
		USER_FIELDS, place_fields=PLACE_FIELDS)


		for tweet_page in response:
			for tweet in ensure_flattened(tweet_page):
				
				try:
					dumped_tweet = self.dumps(tweet); 
					tweet_id = tweet['id']

					lookup_tweet = mongo.f04.tweets.find_one ({'id': tweet_id})

					if not lookup_tweet:
						print(f'Tuíte inserido. TweetID: {tweet_id}\n')
						mongo.f04.tweets.insert_one (json.loads(dumped_tweet))	
					
					#self.write_on_folder(dumped_tweet, tweet_id, base_path)
					
					last_id = tweet_id
					
					if verbose:
						print(f'Tuíte coletado. TweetID: {tweet_id}\n')

				except Exception as e:
					
					raise Exception(f'{e}.\nErro durante a coleta, salvando o ID do último tweet capturado e encerrando.', tweet_id)
