# -*- coding: utf-8 -*-
import math
import numpy as np
import matplotlib.pyplot as plt
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
#from stop_words import get_stop_words
from gensim import corpora, matutils
import gensim
import re
from unicodedata import normalize
import matplotlib
matplotlib.use("agg")


class TextProcessor:
    def tokenize(self, text):
        regex_strings = (

            # Phone numbers:
            r"""
        (?:
          (?:            # (international)
            \+?[01]
            [\-\s.]*
          )?            
          (?:            # (area code)
            [\(]?
            \d{3}
            [\-\s.\)]*
          )?    
          \d{3}          # exchange
          [\-\s.]*   
          \d{4}          # base
        )""",
            # HTML tags:
            r"""<[^>]+>""",
            # Twitter username:
            r"""(?:@[\w_]+)""",
            # Twitter hashtags:
            r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)""",
            # Remaining word types:
            r"""
        (?:[a-z][a-z'\-_]+[a-z])       # Words with apostrophes or dashes.
        |
        (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
        |
        (?:[\w_]+)                     # Words without apostrophes or dashes.
        |
        (?:\S)                         # Everything else that isn't whitespace.
        """)

        word_re = re.compile(r"""(%s)""" % "|".join(regex_strings),
                             re.VERBOSE | re.I | re.UNICODE)
        return word_re.findall(text)

    stoplist = stopwords.words("portuguese")

    # Create p_stemmer of class PorterStemmer
    p_stemmer = SnowballStemmer("portuguese")

    # remvove urls

    def remove_urls(self, txt):
        txt = re.sub(
            r'http\S+',
            '', txt)

        return txt

    def remover_acentos(self, txt):
        return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

    def text_process(self,
                     doc_set,
                     stem=False,
                     text_only=False,
                     lang="portuguese",
                     remove_accent=True,
                     extra_stop_words=[]):
        # list for tokenized documents in loop
        texts = []
        # loop through document list
        for i in doc_set:
            # clean and tokenize document string
            raw = i.lower()

            # remove urls
            raw = self.remove_urls(raw)

            # remove acentos
            if remove_accent:
                raw = self.remover_acentos(raw)

            self.stoplist = self.stoplist + extra_stop_words
            tokens = self.tokenize(raw)

            if lang == "english":
                self.stoplist = stopwords.words("english")
                self.p_stemmer = SnowballStemmer("english")

            # remove os acentos das palavras da stop list
            self.stoplist = [self.remover_acentos(i) for i in self.stoplist]
            # remove stop words from tokens
            stopped_tokens = [i for i in tokens if not i in self.stoplist]

            # remove unigrams and bigrams
            stopped_tokens = [i for i in stopped_tokens if len(i) > 2]

            if stem:
                # stem tokens
                stopped_tokens = [
                    self.p_stemmer.stem(i) for i in stopped_tokens
                ]
            if text_only:
                # remove mentions and hashtags
                stopped_tokens = [
                    term for term in stopped_tokens
                    if not term.startswith(('#', '@'))
                ]

            # add tokens to list
            texts.append(stopped_tokens)

        return texts

    def create_corpus(self, texts):
        # turn our tokenized documents into a id <-> term dictionary
        dictionary = corpora.Dictionary(texts)
        dictionary.compactify()
        # and save the dictionary for future use
        # dictionary.save('tweet_teste.dict')

        # convert tokenized documents into a document-term matrix
        corpus = [dictionary.doc2bow(text) for text in texts]

        # and save in Market Matrix format
        #corpora.MmCorpus.serialize('tweet_teste.mm', corpus)
        # this corpus can be loaded with corpus = corpora.MmCorpus('tweet_teste.mm')
        return (corpus, dictionary)

    def generate_lda(self, corpus, dictionary, num_topics):

        # generate LDA model
        ldamodel = gensim.models.ldamodel.LdaModel(corpus,
                                                   num_topics=num_topics,
                                                   id2word=dictionary,
                                                   alpha='auto')
        # ldamodel.save('tweet_teste.lda')
        #model = gensim.models.LdaModel.load('android.lda')
        print(ldamodel.print_topics())
        # ldamodel.print_topics()
        return ldamodel

    def generate_hdp(self, corpus, dictionary):

        # generate LDA model
        hdpmodel = gensim.models.HdpModel(corpus, id2word=dictionary)
        # ldamodel.save('tweet_teste.lda')
        #model = gensim.models.LdaModel.load('android.lda')
        print(hdpmodel.print_topics(topics=-1, topn=20))
        # ldamodel.print_topics()
        return hdpmodel

    def print_topics(self, ldamodel, topn=10):

        Lambda = ldamodel.state.get_lambda()

        Phi = Lambda / Lambda.sum(axis=1)[:, np.newaxis]
        Phi2 = Lambda / Lambda.sum(axis=0)[np.newaxis, :]
        entropy = np.zeros(Phi2.shape[1])
        topics = ""

        # calcula a entropia Ew≜∑kp(k|w)logp(k|w)
        for w in range(Phi2.shape[1]):
            for k in range(Phi2.shape[0]):
                entropy[w] += Phi2[k, w] * np.log2(Phi2[k, w] + 1e-100)
        print(entropy)

        # calcula p(w|k)e−Hw
        for k in range(Phi.shape[0]):
            for w in range(Phi.shape[1]):
                Phi[k, w] = Phi[k, w] / pow(math.e, (-1) * entropy[w])
        for k in range(Phi.shape[0]):
            bestn = matutils.argsort(Phi[k], topn, reverse=True)
            topic_terms = [(id, Phi[k, id]) for id in bestn]
            lda_words = [(ldamodel.id2word[id], value)
                         for id, value in topic_terms]
            topics += ' + '.join(['%.3f*%s' % (v, k)
                                  for k, v in lda_words]) + "\n"
        return topics
