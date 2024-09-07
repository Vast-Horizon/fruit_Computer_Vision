import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras.callbacks import EarlyStopping

# Load the initial model
model = load_model('fine_tuned_model.h5')

# Unfreeze some layers of the base model
for layer in model.layers[-20:]:  # Unfreezing the last 10 layers as an example
    if not isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = True

# Recompile the model with a lower learning rate
model.compile(optimizer=Adam(learning_rate=1e-5), loss='categorical_crossentropy', metrics=['accuracy'])

# Prepare the dataset (assuming the same dataset paths as before)
train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

# Training data generator
train_generator = train_datagen.flow_from_directory(
    'dataset/kritik_seth/train',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

# Validation data generator
validation_generator = test_datagen.flow_from_directory(
    'dataset/kritik_seth/validation',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Fine-tune the model
fine_tune_history = model.fit(train_generator, epochs=5, validation_data=validation_generator, callbacks=[early_stopping])

# Save the fine-tuned model to a file
model.save('fine_tuned_model_2.h5')

# Convert history to pandas DataFrame
history_df = pd.DataFrame(fine_tune_history.history)

# Plot fine-tuning training & validation accuracy values
plt.figure(figsize=(12, 6))
plt.plot(history_df['accuracy'], label='Fine-Tuning Training Accuracy')
plt.plot(history_df['val_accuracy'], label='Fine-Tuning Validation Accuracy')
plt.title('Fine-Tuning Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='upper left')
plt.grid(True)
plt.show()

# Plot fine-tuning training & validation loss values
plt.figure(figsize=(12, 6))
plt.plot(history_df['loss'], label='Fine-Tuning Training Loss')
plt.plot(history_df['val_loss'], label='Fine-Tuning Validation Loss')
plt.title('Fine-Tuning Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.grid(True)
plt.show()
