from keras.preprocessing.sequence import pad_sequences
from keras.models import Model, load_model
import numpy as np
from models.HAN import Attention
from tensorflow.keras import regularizers
from keras import initializers


class PoliticalClassification:

    def __init__(self, arg_model, dictfile, maxlen):

        self.maxlen = maxlen
        self.model = load_model(arg_model, custom_objects={
                                'word_attention': Attention, 'sentence_attention': Attention, 'L2': regularizers.L2, 'GlorotUniform': initializers.get('glorot_uniform')})
        self.model.compile(loss='binary_crossentropy',
                           optimizer='adam', metrics=['accuracy'])
        self.vocab = np.load(dictfile, allow_pickle=True).item()

    def is_political(self, text):
        X = list()
        seq = list()
        for word in text.split(' '):
            seq.append(self.vocab.get(word, self.vocab['UNK']))
        X.append(seq)
        data = pad_sequences(X, maxlen=self.maxlen)
        y_pred = self.model.predict(data)
        y_pred = np.argmax(y_pred, axis=1)
        return True if y_pred == 1 else False

    def is_political_prob(self, text, metalearner=False):
        X = list()
        seq = list()

        for word in text.split(' '):
            seq.append(self.vocab.get(word, self.vocab['UNK']))
        X.append(seq)

        data = pad_sequences(X, maxlen=self.maxlen)

        if metalearner:
            X_v = [data for _ in range(len(self.model.input))]
            data = X_v

        y_pred = self.model.predict(data)
        return y_pred[0, 1]

    def is_political_prob_han(self, text):

        X = np.zeros((1, 9, self.maxlen), dtype='int32')

        for k, word in enumerate(text):
            if k < self.max_seq_length:
                X[1][0][k] = self.vocab.get(word, self.vocab['UNK'])

        data = pad_sequences(X, maxlen=self.maxlen)

        y_pred = self.model.predict(data)

        return y_pred[0, 1]
