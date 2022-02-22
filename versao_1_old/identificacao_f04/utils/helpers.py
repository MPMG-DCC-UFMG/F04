import numpy as np

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
