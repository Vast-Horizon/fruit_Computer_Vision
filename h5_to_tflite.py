"""
Convert the model to TensorFlow Lite format with dynamic range quantization
"""
import tensorflow as tf

model = tf.keras.models.load_model('fine_tuned_model_4.h5')

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

with open('fine_tuned_model_4.tflite', 'wb') as f:
    f.write(tflite_model)
