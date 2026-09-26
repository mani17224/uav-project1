import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


TIMESTEPS = 20
FEATURES = 21
EMBEDDING_DIM = 128
NUM_HEADS = 4
FF_DIM = 256
DROPOUT = 0.1


class PositionalEmbedding(layers.Layer):
    def __init__(self, timesteps, embedding_dim, **kwargs):
        super().__init__(**kwargs)
        self.projection = layers.Dense(embedding_dim)
        self.position_embedding = layers.Embedding(
            input_dim=timesteps,
            output_dim=embedding_dim
        )
        self.timesteps = timesteps

    def call(self, inputs):
        positions = tf.range(start=0, limit=self.timesteps, delta=1)
        x = self.projection(inputs)
        positions = self.position_embedding(positions)
        return x + positions


def transformer_block(x):
    attention_output = layers.MultiHeadAttention(
        num_heads=NUM_HEADS,
        key_dim=EMBEDDING_DIM // NUM_HEADS,
        dropout=DROPOUT
    )(x, x)

    x = layers.LayerNormalization(epsilon=1e-6)(x + attention_output)

    ff = layers.Dense(FF_DIM, activation="relu")(x)
    ff = layers.Dropout(DROPOUT)(ff)
    ff = layers.Dense(EMBEDDING_DIM)(ff)

    return layers.LayerNormalization(epsilon=1e-6)(x + ff)


def build_transformer():
    inputs = keras.Input(
        shape=(TIMESTEPS, FEATURES),
        name="uav_telemetry"
    )

    x = PositionalEmbedding(
        TIMESTEPS,
        EMBEDDING_DIM
    )(inputs)

    x = transformer_block(x)
    x = transformer_block(x)

    x = layers.GlobalAveragePooling1D()(x)

    embeddings = layers.Dense(
        EMBEDDING_DIM,
        activation=None,
        name="uav_embedding"
    )(x)

    return keras.Model(
        inputs,
        embeddings,
        name="UAV_Transformer_Encoder"
    )


if __name__ == "__main__":
    model = build_transformer()
    model.summary()
    print("\nTransformer model created successfully.")
