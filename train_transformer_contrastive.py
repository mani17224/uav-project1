import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from transformer_model import build_transformer


INPUT_FILE = "processed_data/transformer_contrastive_views.npz"
OUTPUT_MODEL = "processed_data/uav_transformer_encoder.keras"

BATCH_SIZE = 32
EPOCHS = 50
TEMPERATURE = 0.1


def normalize_embeddings(x):
    return tf.math.l2_normalize(x, axis=1)


def contrastive_loss(z1, z2):
    z1 = normalize_embeddings(z1)
    z2 = normalize_embeddings(z2)

    logits = tf.matmul(z1, z2, transpose_b=True)
    logits = logits / TEMPERATURE

    batch_size = tf.shape(logits)[0]
    labels = tf.range(batch_size)

    loss_1 = tf.keras.losses.sparse_categorical_crossentropy(
        labels,
        logits,
        from_logits=True
    )

    loss_2 = tf.keras.losses.sparse_categorical_crossentropy(
        labels,
        tf.transpose(logits),
        from_logits=True
    )

    return tf.reduce_mean((loss_1 + loss_2) / 2.0)


class ContrastiveTrainer(keras.Model):

    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder

        self.loss_tracker = keras.metrics.Mean(
            name="contrastive_loss"
        )

    @property
    def metrics(self):
        return [self.loss_tracker]

    def train_step(self, data):
        view1, view2 = data

        with tf.GradientTape() as tape:
            z1 = self.encoder(view1, training=True)
            z2 = self.encoder(view2, training=True)

            loss = contrastive_loss(z1, z2)

        gradients = tape.gradient(
            loss,
            self.encoder.trainable_variables
        )

        self.optimizer.apply_gradients(
            zip(gradients, self.encoder.trainable_variables)
        )

        self.loss_tracker.update_state(loss)

        return {
            "contrastive_loss": self.loss_tracker.result()
        }


def main():

    print("========================================")
    print("UAV TRANSFORMER CONTRASTIVE TRAINING")
    print("========================================")

    data = np.load(INPUT_FILE)

    view1 = data["view1"].astype(np.float32)
    view2 = data["view2"].astype(np.float32)

    print("View 1:", view1.shape)
    print("View 2:", view2.shape)

    dataset = tf.data.Dataset.from_tensor_slices(
        (view1, view2)
    )

    dataset = dataset.shuffle(
        buffer_size=len(view1),
        seed=42,
        reshuffle_each_iteration=True
    )

    dataset = dataset.batch(BATCH_SIZE)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)

    encoder = build_transformer()

    trainer = ContrastiveTrainer(encoder)

    trainer.compile(
        optimizer=keras.optimizers.Adam(
            learning_rate=0.0005
        )
    )

    print("\nStarting training...")

    trainer.fit(
        dataset,
        epochs=EPOCHS
    )

    encoder.save(OUTPUT_MODEL)

    print("\n========================================")
    print("TRAINING COMPLETED")
    print("========================================")
    print("Saved:", OUTPUT_MODEL)


if __name__ == "__main__":
    main()
