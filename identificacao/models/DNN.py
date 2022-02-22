from models.DeepModel import DeepModel
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
import numpy as np


class DNN(DeepModel):

    def __init__(self, *args, **kwargs):
        super(DNN, self).__init__(*args, **kwargs)

    @property
    def model_name(self):
        return str(self.__class__.__name__)

    def build_model(self):
        self.model = None
        self.model = Sequential()
        node = 512  # number of nodes
        nLayers = 4  # number of  hidden layer
        dropout = 0.5

        self.model.add(
            Dense(node, input_dim=self.word_embed_dim, activation='relu'))
        self.model.add(Dropout(dropout))
        for i in range(0, nLayers):
            self.model.add(Dense(node, input_dim=node, activation='relu'))
            self.model.add(Dropout(dropout))

        self.model.add(Dense(self.num_classes, activation='softmax'))

    def gen_sequence(self, texts, tx_class):
        y_map = dict()
        for i, v in enumerate(sorted(set(tx_class))):
            y_map[v] = i
        print(y_map)

        X, y = [], []
        for i, text in enumerate(texts):
            emb = np.zeros(self.word_embed_dim)
            for word in text:
                try:
                    emb += self.embeddings_index[word]
                except Exception as e:
                    print(e)
                    pass

            if not len(text):
                # only links
                print(i, texts[i])
                continue

            emb /= len(text)

            X.append(emb)
            y.append(y_map[tx_class[i]])

        return X, y
