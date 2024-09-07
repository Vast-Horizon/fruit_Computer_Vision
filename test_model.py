import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Load the saved model
model = tf.keras.models.load_model(r'fine_tuned_model_4.h5')

# Prepare the test dataset
test_datagen = ImageDataGenerator(rescale=1./255)

# Test data generator
test_generator = test_datagen.flow_from_directory(
    r'dataset/kritik_seth/test',
    target_size=(224, 224),  # Use the same target size as during training
    batch_size=32,
    class_mode='categorical',
    shuffle=False
)

# Evaluate the model on the test dataset
test_loss, test_accuracy = model.evaluate(test_generator)

print(f"Test Loss: {test_loss}")
print(f"Test Accuracy: {test_accuracy}")
