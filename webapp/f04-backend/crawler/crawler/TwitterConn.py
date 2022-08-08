import json
import time
import datetime as date

from twarc.client2 import Twarc2

class TwitterConn():
	def __init__(self, configuration_file):
		self.__api = list()
		
		self.curr = 0

		self.__authenticate(configuration_file['access_keys'])


	def __authenticate(self, key_set):
			""" Method responsible to authenticate the API keys and store in the class.

			Args:
					key_set (list of dictionaries): Contains the keys to communicate with the API.

			Raises:
					Exception: Invalid or missing keys for Twitter's API authentication.
			"""
			for item in key_set:
					try:
							api_object = Twarc2(bearer_token=item['bearer_token']) 

							self.__api.append(api_object)

					except Exception:
							print(f"Invalid keys: \n{key_set}\n ")

			if len(self.__api) == 0:
					raise Exception("Invalid or missing keys for Twitter's API authentication in the configuration file.")

	def __next_api(self):
			"""Change to the next key"""
			self.curr = (self.curr + 1) % (len(self.__api))

	def get_next_api(self):
				
		return self.__api[self.curr]


	# Tratamento de chaves removido, pois a biblioteca Twarc gerencia automaticamente as chaves disponíveis.

	# def __rate_limit(self):
	# 		API_TIME_RESET = 901 #Seconds
	# 		API_TIME_SLEEP = 5 #Seconds

	# 		while True:
	# 				time_window = date.datetime.now() - self.times[self.curr]

	# 				if time_window.seconds >= API_TIME_RESET:
	# 						break
	# 				else:
	# 						time.sleep(API_TIME_SLEEP)
	# 						self.__next_api()

	# 		self.times[self.curr] = date.datetime.now()

	# 		print("Changed Keys")  

	# def __treat_exhausted_keys(self):
	# 		del self.__api[self.curr]
			
	# 		del self.times[self.curr]

	# 		if len(self.__api) == 0:
	# 				raise Exception('All keys are exhausted.')    

	# 		self.__next_api()

	# def remove_current_api(self):
	# 	"""
	# 	Remove actual api and return next.
	# 	"""
	# 	self.__treat_exhausted_keys()
	# 	return self.__api[self.curr]

