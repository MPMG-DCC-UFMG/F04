from models.DeepModel import DeepModel
from keras.models import Sequential
from keras.layers import Embedding, LSTM
from keras.layers.core import Dense

class LSTMC(DeepModel):

    def __init__(self, *args, **kwargs):
        super(LSTMC, self).__init__(*args, **kwargs)
    
    @property
    def model_name (self):
        return str(self.__class__.__name__)

    def build_model (self):
        self.model = None
        
        self.model = Sequential()
        self.model.add(Embedding(len(self.vocab) + 1, self.word_embed_dim,
                    input_length=self.max_seq_length, weights=[self.get_embedding_matrix()], trainable=False))
        self.model.add(LSTM(self.word_embed_dim))

        self.model.add(Dense(self.num_classes, activation='sigmoid'))
