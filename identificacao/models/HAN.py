from models.DeepModel import DeepModel
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Embedding, Input, Bidirectional, LSTM, Layer, TimeDistributed, Lambda
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras import regularizers
from tensorflow.keras import initializers
import tensorflow.keras.backend as K
import numpy as np
import pandas as pd
from utils.helpers import log
import tensorflow as tf


@tf.keras.utils.register_keras_serializable()
class Attention(Layer):
    def __init__(self, *args, **kwargs):

        self.regularizer = regularizers.l2(1e-8)
        self.supports_masking = True
        self.init = initializers.get('glorot_uniform')
        super(Attention, self).__init__(*args, **kwargs)

    def build(self, input_shape):
        # Create a trainable weight variable for this layer.
        self.context = self.add_weight(name='context', shape=(input_shape[-1], 1), initializer=self.init,
                                       regularizer=self.regularizer, trainable=True)
        super(Attention, self).build(input_shape)

    def call(self, x, mask=None):
        attention_in = K.exp(K.squeeze(K.dot(x, self.context), axis=-1))
        attention = attention_in / \
            K.expand_dims(K.sum(attention_in, axis=-1), -1)

        if mask is not None:
            # use only the inputs specified by the mask
            attention = attention * K.cast(mask, 'float32')

        weighted_sum = K.batch_dot(
            K.permute_dimensions(x, [0, 2, 1]), attention)
        return weighted_sum

    def compute_output_shape(self, input_shape):

        return input_shape[0], input_shape[-1]

    def get_config(self):

        config = super(Attention, self).get_config()
        config.update({
            # 'regularizer': self.regularizer,
            # 'supports_masking': self.supports_masking,
            # 'init': self.init
        })

        return config


class HAN(DeepModel):

    def __init__(self, *args, **kwargs):
        super(HAN, self).__init__(*args, **kwargs)
        self.max_seq_num = 9
        self.pad_sequences = False

    @property
    def model_name(self):
        return str(self.__class__.__name__)

    def build_model(self):
        self.model = None

        embedding_layer = Embedding(len(self.vocab) + 1, self.word_embed_dim, weights=[self.get_embedding_matrix()],
                                    input_length=self.max_seq_length, trainable=False, name='word_embedding')

        # model = Model(text_input, preds)
        l2_reg = regularizers.l2(1e-8)
        sentence_in = Input(shape=(self.max_seq_length,), dtype='int32')
        embedded_word_seq = embedding_layer(sentence_in)

        # return sequences True to return the hidden state output for each input time step.
        word_encoder = Bidirectional(
            LSTM(int(self.word_embed_dim/2), return_sequences=True))(embedded_word_seq)
        dense_transform_w = Dense(
            self.word_embed_dim, activation='relu', name='dense_transform_w', kernel_regularizer=l2_reg)(word_encoder)
        att_layer = Attention(name='word_attention')(dense_transform_w)
        self.word_model = Model(sentence_in, att_layer)

        self.word_model.summary()

        # Generate sentence-attention-weighted document scores
        texts_in = Input(
            shape=(self.max_seq_num, self.max_seq_length), dtype='int32')

        self.word_models = TimeDistributed(
            self.word_model)(texts_in)
        sentence_encoder = Bidirectional(
            LSTM(int(self.word_embed_dim/2), return_sequences=True))(self.word_models)
        dense_transform_s = Dense(
            self.word_embed_dim, activation='relu', name='dense_transform_s', kernel_regularizer=l2_reg)(sentence_encoder)
        attention_weighted_text = Attention(
            name='sentence_attention')(dense_transform_s)
        prediction = Dense(2, activation='softmax')(attention_weighted_text)
        self.model = Model(texts_in, prediction)

    def bert_preprocessing(self, files, sep=';', randomize=True):
        self.max_seq_length = self.word_embed_dim
        X, Y = super().bert_preprocessing(files, sep, randomize)
        Xhan = np.zeros(
            (X.shape[0], 9, self.max_seq_length), dtype='float64')
        log('Han reshape: %s' % str(Xhan.shape))
        for i, bert_encoded in enumerate(X):

            for k in range(0, self.max_seq_length):
                print(i, bert_encoded[k])
                Xhan[i][0][k] = bert_encoded[k]

        return Xhan, Y

    def gen_sequence(self, texts, tx_class):
        y_map = dict()

        for i, v in enumerate(sorted(set(tx_class))):
            y_map[v] = i
        print(y_map)
        y = []
        X = np.zeros((len(texts), 9, self.max_seq_length), dtype='int32')
        for i, text in enumerate(texts):
            seq = []

            for k, word in enumerate(text):
                if k < self.max_seq_length:
                    seq.append(self.vocab.get(word, self.vocab['UNK']))
                    X[i][0][k] = self.vocab.get(word, self.vocab['UNK'])

            y.append(y_map[tx_class[i]])

        return X, y

    def show_word_attention(self, x):
        """Show the prediction of the word level attention.
        Args:
            x: the input array with size of (max_sent_length,).
        Returns:
            Attention weights.
        """
        att_layer = self.model_word.get_layer('word_attention')
        prev_tensor = att_layer.input

        # Create a temporary dummy layer to hold the
        # attention weights tensor
        dummy_layer = Lambda(
            lambda x: att_layer._get_attention_weights(x)
        )(prev_tensor)

        return Model(self.model_word.input, dummy_layer).predict(x)

    def show_sent_attention(self, x):
        """Show the prediction of the sentence level attention.
        Args:
            x: the input array with the size of (max_sent_num, max_sent_length).
        Returns:
            Attention weights.
        """
        att_layer = self.model.get_layer('sentence_attention')
        prev_tensor = att_layer.input

        dummy_layer = Lambda(
            lambda x: att_layer._get_attention_weights(x)
        )(prev_tensor)

        return Model(self.model.input, dummy_layer).predict(x)

    @staticmethod
    def word_att_to_df(sent_tokenized_document, word_att):
        """Convert the word attention arrays into pandas dataframe.
        Args:
            sent_tokenized_document: sentence tokenized document, which means sent_tokenize(document)
                has to be executed beforehand. And only one document is allowed, since it's
                on word attention level, and also it's the required input size in
                self.show_word_attention, but document can contain multiple sentences.
            word_att: attention weights obtained from self.show_word_attention.
        Returns:
            df: pandas.DataFrame, contains original documents column and word_att column,
                and word_att column is a list of dictionaries in which word as key while
                corresponding weight as value.
        """
        # remove the trailing dot
        ori_sents = [i.rstrip('.') for i in sent_tokenized_document]
        # split sentences into words
        ori_words = [x.split() for x in ori_sents]
        # truncate attentions to have equal size of number of words per sentence
        truncated_att = [i[-1 * len(k):] for i, k in zip(word_att, ori_words)]

        # create word attetion pair as dictionary
        word_att_pair = []
        for i, j in zip(truncated_att, ori_words):
            word_att_pair.append(dict(zip(j, i)))

        return pd.DataFrame([(x, y) for x, y in zip(word_att_pair, ori_words)],
                            columns=['word_att', 'document'])

    @staticmethod
    def sent_att_to_df(sent_tokenized_documents, sent_att):
        """Convert the sentence attention arrays into pandas dataframe.
        Args:
            sent_tokenized_documents: sent tokenized documents, if original input is a Series,
                that means at least Series.apply(lambda x: sent_tokenize(x)) has to be
                executed beforehand.
            sent_att: sentence attention weight obtained from self.show_sent_attetion.
        Returns:
            df: pandas.DataFrame, contains original documents column and sent_att column,
                and sent_att column is a list of dictionaries in which sentence as key
                while corresponding weight as value.
        """
        # create documents attention pair list
        documents_atts = []
        for document, atts in zip(sent_tokenized_documents, sent_att):
            document_list = []
            for sent, att in zip(document, atts):
                # each is a list of dictionaries
                document_list.append({sent: att})
            documents_atts.append(document_list)
        return pd.DataFrame([(x, y) for x, y in zip(documents_atts, sent_tokenized_documents)],
                            columns=["sent_att", "document"])
