import tensorflow as tf
from tensorflow import keras
from modules import *
from dataset import *

# load the data using the data processor
train_ds, valid_ds, test_ds = process_data()

# create call backs for early stopping and saving the weights
early_stopper= keras.callbacks.EarlyStopping(monitor="loss", patience=10)
checkpoint_filepath = "./weights"
model_checkpoint = keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=True,
    monitor="loss",
    mode="min",
    save_best_only=True,
)

# get the model and compile using a mean squared error loss function
model = get_model()
model.summary()

callbacks = [early_stopper, model_checkpoint]
loss_function= keras.losses.MeanSquaredError()
optimizer = keras.optimizers.Adam(learning_rate=0.001)

model.compile(optimizer=optimizer, loss=loss_function, metrics=['acc'])

result = model.fit(train_ds, epochs=50, callbacks=callbacks, validation_data=valid_ds, verbose=2)

# plot the accuracy from training
plt.plot(result.history['acc'])
plt.plot(result.history['val_acc'])
plt.ylabel('Accuracy')
plt.xlabel('epoch')
plt.savefig("acc.jpg")

# plot the loss from training
plt.plot(result.history['loss'])
plt.plot(result.history['val_loss'])
plt.ylabel('loss')
plt.xlabel('epoch')
plt.savefig("loss.jpg")

# load the best weights and save the model
model.load_weights(checkpoint_filepath)
model.save("trained_model")

# save the test data to be used later for predictions
test_ds.save("test_data")
