import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from models.DeepModel import DeepModel
import time
"""
## Implement a Transformer block as a layer
"""


class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim)
        self.ffn = keras.Sequential(
            [layers.Dense(ff_dim, activation="relu"),
             layers.Dense(embed_dim), ]
        )
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


"""
## Implement embedding layer
Two seperate embedding layers, one for tokens, one for token index (positions).
"""


class TokenAndPositionEmbedding(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding, self).__init__()
        self.token_emb = layers.Embedding(
            input_dim=vocab_size, output_dim=embed_dim)
        self.pos_emb = layers.Embedding(input_dim=maxlen, output_dim=embed_dim)

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions


class Transformer(DeepModel):

    def __init__(self, *args, **kwargs):
        super(Transformer, self).__init__(*args, **kwargs)

    @property
    def model_name(self):
        return str(self.__class__.__name__)

    def build_model(self):
        self.model = None

        """
        ## Create classifier model using transformer layer
        Transformer layer outputs one vector for each time step of our input sequence.
        Here, we take the mean across all time steps and
        use a feed forward network on top of it to classify text.
        """

        embed_dim = 32  # Embedding size for each token
        num_heads = 2  # Number of attention heads
        ff_dim = 32  # Hidden layer size in feed forward network inside transformer

        inputs = layers.Input(shape=(self.max_seq_length,))
        embedding_layer = TokenAndPositionEmbedding(
            self.max_seq_length, len(self.vocab)+1, self.word_embed_dim)
        x = embedding_layer(inputs)
        transformer_block = TransformerBlock(
            self.word_embed_dim, num_heads, ff_dim)
        x = transformer_block(x)
        x = layers.GlobalAveragePooling1D()(x)
        x = layers.Dropout(0.1)(x)
        x = layers.Dense(20, activation="relu")(x)
        x = layers.Dropout(0.1)(x)
        outputs = layers.Dense(2, activation="softmax")(x)

        self.model = keras.Model(inputs=inputs, outputs=outputs)
        time.sleep(30)
