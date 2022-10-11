"""train.py

The source code for traiing, validating, testing, and saving the model.
"""

from constants import CHECKPOINT_FILEPATH
from modules import get_model, ESPCNCallback
from dataset import downsample_data, get_image_from_dataset, preview_data

import tensorflow as tf
from tensorflow import keras

def train_model(
    train_ds: tf.data.Dataset,
    test_ds: tf.data.Dataset,
    epochs: int,
    checkpoint: str | None = None,
) -> keras.Model:
    """Train the super-resolution model, saving the best checkpoint

    Args:
        train_ds (tf.data.Dataset): high-res training dataset
        test_ds (tf.data.Dataset): high-res testing dataset
        epochs (int): number of epochs to train for
        checkpoint (str | None): Optional path to a checkpoint file. If given,
            the model will use the checkpoint specified instead of training from
            the beginning. Defaults to None.

    Returns:
        keras.Model: The trained model
    """
    down_train_ds = downsample_data(train_ds)
    down_test_ds = downsample_data(test_ds)

    preview_data(train_ds, "High res training dataset")
    preview_data(test_ds, "High res testing dataset")
    preview_data(down_train_ds, "Low res training dataset")
    preview_data(down_test_ds, "Low res testing dataset")

    early_stopping_callback = keras.callbacks.EarlyStopping(
        monitor="loss",
        patience=10
    )

    model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
        filepath=CHECKPOINT_FILEPATH,
        save_weights_only=True,
        monitor="loss",
        mode="min",
        save_best_only=True,
    )

    model = get_model()
    model.summary()

    if checkpoint:
        model.load_weights(checkpoint)
        print(f"Loaded checkpoint weights from {checkpoint} into model")

    test_image = get_image_from_dataset(test_ds)

    callbacks = [
        ESPCNCallback(test_image),
        early_stopping_callback,
        model_checkpoint_callback
    ]
    loss_fn = keras.losses.MeanSquaredError()
    optimizer = keras.optimizers.Adam(learning_rate=0.001)

    model.compile(
        optimizer=optimizer,
        loss=loss_fn,
    )

    model.fit(
        down_train_ds,
        epochs=epochs,
        callbacks=callbacks,
        validation_data=down_test_ds,
        verbose=1,
    )

    return model
