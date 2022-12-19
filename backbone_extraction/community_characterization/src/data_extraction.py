import pandas as pd
import numpy as np
import regex as re
from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer, word_tokenize
from itertools import islice
from operator import add
from functools import reduce 

class DataExtraction():

    def __init__(self, list_seeds=None, blocklist_hashtags=None):
        
        self.list_seeds = ["vote para prefeito", "vote no candidato", "vote para deputado", "vote em quem", "conto com o seu voto","ter o seu voto", "vote em candidatos", "quero ser o seu vereador", "vote para prefeita", "vote para deputada", "vote no senador", "vote em mim", "juntos nessa caminhada", "vote nos candidatos", "no dia XX vote", "quero ser seu candidato", "quero ser o seu prefeito",
            "quero ser o seu deputado", "contamos com o seu voto", "quero ser a sua vereadora", "contra a velha política", "conto com o seu apoio", "quero ser o seu presidente", "vote em candidatas", "quero ser sua candidata", "vote na candidata","vote nas candidatas", "vote na senadora", "não vote nele", "não vote nela","quero ser a sua prefeita", "quero ser a sua deputada", "vote em candidato","vote em candidata", "vote em mulher", "trabalhador vota em trabalhador", "seu eu for eleito", "gostaria de pedir seu voto", "votar em mim", "votar em candidatos", "votar em candidato", "votar em candidatas", 
            "votar em candidata", "votar nos candidatos", "votar no candidato", "votar nas candidatas", "votar na candidata", "posso contar com o seu voto"] \
                if not list_seeds else list_seeds

        self.blocklist_hashtags = set(['VaiCorinthians', 'BestFanArmy', 'StrayKids', 'PACAMPEAO', 'ENHYPEN_SUNOO','BestCoverSong', '스트레이키즈', '엔하이픈_선우', 'good4u', '김선우', 'MantoDaMassa', 'FicaPA', 'LatinAMAs', 'PremiosLikesBrasil', '드림캐쳐', 'Dreamcatcher', 'LOONA','ForaEli', 'Vasco', 'ATEEZ', 'ArtistaFavoritoPop', 'bbtvi', '이달의소녀', 'Sweepstakes','BestMusicVideo', 'EstrelaRealityShow', '에이티즈', 'spfcmenosémais', 'MONSTAX','FicaJessi', 'ForaLais', '갓세븐', 'BAEKHYUN', 'Cinderella', 'WONHO', 'FicaScooby', 'ForaLucas', 'ForaVyni', 'GIDLE', 'KEP1ER', '케플러', 'ShapeofLove', 'UKAWARDS', 'KeremBürsin', 'ChapaAzul', 'ibest', 'PIXY', '픽시', 'premioibest', 'premioibest2022','뱀뱀', 'mellos', '백현', '여자아이들', 'Butter', 'HappierThanEver', 'CBLAWARDS','BadBuddySeries', 'SpaceNews', '엔하이픈선우', 'HandeErçel', 'DRPowerCouple', 'BUTTER', 'VICTON', '빅톤', 'EstrelaRalityShow', '원호', 'WOOYOUNG', '우영', 'BillieEilish', 'WONHO_OBSESSION', 'TheGoldenDucket', 'salveotricolorpaulista', 'menosgolpemaisspfc', 'golpespfcnão', 'golpenãospfc', 'TRINITY_TNT', 'NAACPImageAwards', 'LOVE', 'HYUNGWON', 'doutor', 'AnimeAwards', 'WONHO_EYEONYOU', 'WomensRightsAreHumanRights', 'HumanRights', 'GOT7', 'Bambam', 'sem9739aPRFvaimaislonge', 'エンハイフン_ソヌ, 솔라','Leila', 'Volei', 'DF', 'VamosBOTAFOGO', 'TudoIAwards', 'GOOD_BOY_GONE_BAD','SakugaBrasilPOPAwards2022', 'Flamengo', 'UnidosPeloFlamengo', 'LandimPresidente', 'VoteComigoMengao', 'ChapaRoxa', 'OBAwards2021', 'CopagPokemon', 'LoRAwardsBR', 
            'GuriasGremistas', 'BRFeminino2022', 'FutebolGaúcho', 'GrandesHistóriasPassamPorAqui', 'ForaRodrigo', 'FicaEslô', 'SeoHyunJin', 'Cassiopeia', 'ForaDouglas','ForaViny', 'TeamDouglas', '엑소디오', 'Kyungsoo', '도경수', 'TheBatman', 'SakugaBrasilPOPAwards2022',
            'CasaDaChampions', 'MTVMovieAwards', 'MineiroMóduloII','LISA', 'MAMAMOO', '마마무', 'Honey_Solar', '블랙핑크', 'MOONBIN_SANHA', 'DabemeBestTeam', 'OffGun']) \
                if not blocklist_hashtags else blocklist_hashtags

    def extraction_facade(self, twitter_text_list):

        mentions = twitter_text_list.apply(self.extract_mentions)

        keywords = twitter_text_list.apply(self.extract_keyword)

        hashtags = twitter_text_list.apply(self.extract_hashtag)

        return mentions, keywords, hashtags


    def extract_mentions(self, tweet):
        
        # the regular expression
        regex = "(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9_]+)"
        
        # extracting the hashtags
        mentions_list = list(set(re.findall(regex, tweet)))
        return mentions_list


    def extract_keyword(self, tweet):

        tweet = tweet.lower()
        list_kw = []
        for kw in self.list_seeds:
            if kw in tweet:
                list_kw.append(kw)
        if len(list_kw) > 0:
            return list_kw
        else:
            return np.nan    

    def extract_hashtag(self, tweet):
        # the regular expression
        regex = "#(\w+)"
        # extracting the hashtags
        hashtag_list = list(set(re.findall(regex, tweet)))
        if len(hashtag_list) > 0:
            return hashtag_list
        else:
            return np.nan

    def flag_tweet(self, tweet):
        tweet = tweet.lower()
        for hashtag in self.blocklist_hashtags:
            if hashtag.lower() in tweet:
                return 1
        else: 
            return 0
    
    def clean_dataset(self, df):

        df['to_be_removed'] = df['text'].apply(self.flag_tweet)
        
        df = df[df['to_be_removed']== 0]
        
        del df['to_be_removed']
        
        df = df[df['referenced_tweets.retweeted.id'].isnull() == False]

        df_temp = df[['referenced_tweets.retweeted.id','id']].groupby(["referenced_tweets.retweeted.id"]).count().reset_index(drop=False)
        
        set_tweets = set(df_temp[df_temp['id'] > 1]['referenced_tweets.retweeted.id'])
        
        del df_temp
        
        df = df[df['referenced_tweets.retweeted.id'].isin(set_tweets)]
        ##Removing less active users (e.g., only 1 rt at the period analyzed)
        df_temp = df

        df_temp = df_temp[['author_id','id']].groupby(["author_id"]).count().reset_index(drop=False)
        
        set_users = set(df_temp[df_temp['id'] > 1]['author_id'])
        
        df = df[df['author_id'].isin(set_users)]
        
        return df
