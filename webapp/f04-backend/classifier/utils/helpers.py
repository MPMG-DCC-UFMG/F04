import numpy as np
import re
import logging


def gen_data(texts, word2vec_model, EMBEDDING_DIM=300):
    X = []
    i = 0
    for text in texts:
        emb = np.zeros(EMBEDDING_DIM)
        for word in text:
            try:
                emb += word2vec_model[word]
            except:
                pass
        if not len(text):
            print(i, texts[i])

            # continue

        i += 1
        emb /= len(text)
        X.append(emb)
    return X


def log(txt, level='warning'):
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    if level == 'warning':
        logging.warning(txt)
    elif level == 'error':
        logging.error(txt)
    elif level == 'exception':
        logging.exception(txt)
    elif level == 'info':
        logging.info(txt)
