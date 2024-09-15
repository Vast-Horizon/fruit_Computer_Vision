"""
This script is indeed to be used on raspberry pi only.
It predicts the fruits in an image or a folder of images.
"""
import tflite_runtime.interpreter as tflite
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import cv2  # Import OpenCV for image processing

# Load the TensorFlow Lite model
def load_tflite_model(model_path):
    # Load the TensorFlow Lite model as an interpreter
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    return interpreter

# Load the class indices
with open('class_indices.json', 'r') as f:
    class_indices = json.load(f)
class_labels = list(class_indices.keys())

# Preprocess the image using OpenCV
def load_and_preprocess_image(img_path, target_size=(224, 224)):
    img = cv2.imread(img_path)
    img = cv2.resize(img, target_size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
    img_array = np.expand_dims(img, axis=0)  # Add batch dimension
    img_array = img_array.astype('float32') / 255.0  # Rescale the image to [0, 1]
    return img_array

# Make prediction using TensorFlow Lite
def predict_with_tflite(interpreter, processed_image):
    # Get input and output tensors
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
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB for displaying in plt
    plt.imshow(img_rgb)
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

    fig, axes = plt.subplots(rows, cols, figsize=(10, 1 * rows))
    axes = axes.flatten()

    for i, img_filename in enumerate(img_filenames):
        img_path = os.path.join(img_folder_path, img_filename)

        # Preprocess the image
        processed_image = load_and_preprocess_image(img_path)
        predictions = predict_with_tflite(interpreter, processed_image)

        top_index = np.argmax(predictions)
        top_class = class_labels[top_index]
        top_confidence = predictions[top_index]

        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB for displaying in plt
        axes[i].imshow(img_rgb)
        axes[i].set_title(f'{top_class} ({top_confidence:.2f})')
        axes[i].axis('off')

    plt.tight_layout()
    plt.show()

# Load the TFLite model
interpreter = load_tflite_model('fine_tuned_model_4.tflite')

# Uncomment to test with a single image
# image_recognition(interpreter, 'images/Untitled-design-71.png')

# Test with a batch of images
batch_recognition(interpreter)
