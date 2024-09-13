import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from tensorflow.keras.preprocessing import image

print("Tensorflow version:", tf.__version__)

# Load the TensorFlow Lite model
def load_tflite_model(model_path):
    # Load the TensorFlow Lite model as an interpreter
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    return interpreter


# Load the class indices
with open('class_indices.json', 'r') as f:
    class_indices = json.load(f)
class_labels = list(class_indices.keys())


# Preprocess the image
def load_and_preprocess_image(img_path, target_size=(224, 224)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Rescale the image to [0, 1]
    return img_array


# Make prediction using TensorFlow Lite
def predict_with_tflite(interpreter, processed_image):
    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], processed_image.astype(np.float32))
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]

    return predictions


def image_recognition(interpreter, path):
    img_path = path
    processed_image = load_and_preprocess_image(img_path)
    predictions = predict_with_tflite(interpreter, processed_image)

    # Get the top three predictions
    top_indices = np.argsort(predictions)[-3:][::-1]
    top_classes = [class_labels[i] for i in top_indices]
    top_confidences = [predictions[i] for i in top_indices]

    for i in range(3):
        print(f"Prediction {i + 1}: {top_classes[i]} (Confidence: {top_confidences[i]:.2f})")

    # Display the image with the predicted label and confidence score of the top prediction
    plt.imshow(image.load_img(img_path))
    plt.title(f'Top Prediction: {top_classes[0]} ({top_confidences[0]:.2f})')
    plt.axis('off')
    plt.show()


def batch_recognition(interpreter):
    img_folder_path = 'images/extra_test_pics'
    img_filenames = os.listdir(img_folder_path)

    # Prepare a grid to display the images
    num_images = len(img_filenames)
    cols = 5
    rows = (num_images // cols) + int(num_images % cols > 0)

    # Reduce the figure size for smaller subplots
    fig, axes = plt.subplots(rows, cols, figsize=(12, 2.5 * rows))  # Adjust figsize as needed
    axes = axes.flatten()

    for i, img_filename in enumerate(img_filenames):
        img_path = os.path.join(img_folder_path, img_filename)

        # Preprocess the image
        processed_image = load_and_preprocess_image(img_path)
        predictions = predict_with_tflite(interpreter, processed_image)

        top_index = np.argmax(predictions)
        top_class = class_labels[top_index]
        top_confidence = predictions[top_index]

        axes[i].imshow(image.load_img(img_path))
        axes[i].set_title(f'{top_class} ({top_confidence:.2f})')
        axes[i].axis('off')

    # Adjust layout to ensure no overlapping
    plt.tight_layout()
    plt.show()



interpreter = load_tflite_model('fine_tuned_model_4.tflite')

# image_recognition(interpreter, 'images/Untitled-design-71.png')
batch_recognition(interpreter)
