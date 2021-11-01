from models.DeepModel import DeepModel
from keras.models import Model, Sequential
from keras.layers import Embedding, Input, Concatenate, GlobalMaxPooling1D
from keras.layers.convolutional import Convolution1D
from keras.layers.core import Activation
from keras.layers.core import Dropout
from keras.layers.core import Dense


class CNN(DeepModel):

    def __init__(self, *args, **kwargs):
        super(CNN, self).__init__(*args, **kwargs)

    @property
    def model_name(self):
        return str(self.__class__.__name__)

    def build_model(self):
        self.model = None

        # Model Hyperparameters
        filter_sizes = (3, 4, 5)
        num_filters = 120
        dropout_prob = (0.25, 0.25)

        graph_in = Input(shape=(self.max_seq_length, self.word_embed_dim))
        convs = []

        for fsz in filter_sizes:
            conv = Convolution1D(filters=num_filters,
                                 kernel_size=fsz,

                                 activation='relu')(graph_in)

            pool = GlobalMaxPooling1D()(conv)

            convs.append(pool)

        if len(filter_sizes) > 1:
            out = Concatenate()(convs)
        else:
            out = convs[0]

        graph = Model(inputs=graph_in, outputs=out)

        model = Sequential()

        model.add(Embedding(len(self.vocab)+1,
                            self.word_embed_dim,
                            input_length=self.max_seq_length,
                            weights=[self.get_embedding_matrix()],
                            trainable=False))

        model.add(Dropout(dropout_prob[0]))
        model.add(graph)
        model.add(Dropout(dropout_prob[1]))
        model.add(Activation('relu'))
        model.add(Dense(2, activation='sigmoid'))

        self.model = model

        return model
