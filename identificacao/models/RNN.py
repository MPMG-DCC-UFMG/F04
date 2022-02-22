from models.DeepModel import DeepModel
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GRU
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
import tensorflow as tf


class RNN(DeepModel):

    def __init__(self, *args, **kwargs):
        super(RNN, self).__init__(*args, **kwargs)

    @property
    def model_name(self):
        return str(self.__class__.__name__)

    def build_model(self):
        self.model = Sequential()

        hidden_layer = 3
        gru_node = 32
        dropout = 0.2

        if self.initialize_weights_with == 'word2vec':
            self.model.add(Embedding(len(self.vocab) + 1,
                                     self.word_embed_dim,
                                     weights=[self.get_embedding_matrix()],
                                     input_length=self.max_seq_length,
                                     trainable=False))
        else:
            self.model.add(tf.keras.layers.Reshape(
                (1, self.word_embed_dim), input_shape=(self.word_embed_dim,)))

            # self.model.add(Dropout(dropout))

        for i in range(0, hidden_layer):
            self.model.add(GRU(gru_node, return_sequences=True))
            self.model.add(Dropout(dropout))

        self.model.add(GRU(gru_node))
        self.model.add(Dropout(dropout))
        self.model.add(Dense(256, activation='relu'))
        self.model.add(Dense(self.num_classes, activation='softmax'))
