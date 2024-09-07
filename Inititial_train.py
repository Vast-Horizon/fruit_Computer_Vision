import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, MaxPooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import pandas as pd
import json

# I need for images that shows fruits in basket and plastic packaging

# Prepare the dataset
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(rescale=1./255)

# Training data generator
train_generator = train_datagen.flow_from_directory(
    'dataset/kritik_seth/train',
    target_size=(224, 224), # resizing the images to 224x224 as a standard
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

# Test data generator (optional if you want to evaluate on a test set later)
test_generator = test_datagen.flow_from_directory(
    'dataset/kritik_seth/test',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

# Save the class indices
class_indices = train_generator.class_indices
with open('class_indices.json', 'w') as f:
    json.dump(class_indices, f)

# Load pre-trained model
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Freeze all layers, except last layer
# The goal is to train just last layer of pre trained model
base_model.trainable = True
set_trainable = False

for layer in base_model.layers :
    if layer.name == 'block_16_expand' :
        set_trainable = True
        print('at block_16_expand')
    if set_trainable :
        layer.trainable = True
    else :
        layer.trainable = False

# Add custom layers
x = base_model.output

# MaxPooling layer for additional downsampling
x = MaxPooling2D(pool_size=(2, 2))(x)

# Global Average Pooling layer to reduce dimensionality
x = GlobalAveragePooling2D()(x)

# Fully connected layers
x = Dense(1024, activation='relu')(x)
predictions = Dense(train_generator.num_classes, activation='softmax')(x)  # Output layer. num_classes is dynamically determined
model = Model(inputs=base_model.input, outputs=predictions)

# # Freeze base layers
# for layer in base_model.layers:
#     layer.trainable = False

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])

early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Train the model and store the history
history = model.fit(
    train_generator,
    epochs=20,
    validation_data=validation_generator,
    callbacks=[early_stopping]
)

# Save the trained model to a file
model.save('initial_model.h5')

# Convert history to pandas DataFrame
history_df = pd.DataFrame(history.history)

# Plot training & validation accuracy values
plt.figure(figsize=(12, 6))
plt.plot(history_df['accuracy'], label='Training Accuracy')
plt.plot(history_df['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='upper left')
plt.grid(True)
plt.show()

# Plot training & validation loss values
plt.figure(figsize=(12, 6))
plt.plot(history_df['loss'], label='Training Loss')
plt.plot(history_df['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.grid(True)
plt.show()
