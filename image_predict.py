import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# Load the fine-tuned model
model = load_model('fine_tuned_model_4.h5')

# Load the class indices
with open('class_indices.json', 'r') as f:
    class_indices = json.load(f)
class_labels = list(class_indices.keys())

# Load and preprocess the image
def load_and_preprocess_image(img_path, target_size=(224, 224)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Rescale the image to [0, 1]
    return img_array

def image_recognition(path):
    # Select the image path
    img_path = path

    # Preprocess the image
    processed_image = load_and_preprocess_image(img_path)

    # Make prediction
    predictions = model.predict(processed_image)

    # Get the top three predictions
    top_indices = np.argsort(predictions[0])[-3:][::-1]
    top_classes = [class_labels[i] for i in top_indices]
    top_confidences = [predictions[0][i] for i in top_indices]

    # Print the top three predictions with confidence scores
    for i in range(3):
        print(f"Prediction {i+1}: {top_classes[i]} (Confidence: {top_confidences[i]:.2f})")

    # Display the image with the predicted label and confidence score of the top prediction
    plt.imshow(image.load_img(img_path))
    plt.title(f'Top Prediction: {top_classes[0]} ({top_confidences[0]:.2f})')
    plt.axis('off')
    plt.show()

def batch_recognition():
    # Select the image folder
    img_folder_path = 'images/my_pic'
    img_filenames = os.listdir(img_folder_path)

    # Prepare a grid to display the images
    num_images = len(img_filenames)
    cols = 5  # Number of images per row
    rows = (num_images // cols) + int(num_images % cols > 0)

    # Set up the figure for plotting
    fig, axes = plt.subplots(rows, cols, figsize=(15, 3 * rows))
    axes = axes.flatten()

    for i, img_filename in enumerate(img_filenames):
        img_path = os.path.join(img_folder_path, img_filename)

        # Preprocess the image
        processed_image = load_and_preprocess_image(img_path)

        # Make prediction
        predictions = model.predict(processed_image)

        # Get the top prediction
        top_index = np.argmax(predictions[0])
        top_class = class_labels[top_index]
        top_confidence = predictions[0][top_index]

        # Display the image with the predicted label and confidence score
        axes[i].imshow(image.load_img(img_path))
        axes[i].set_title(f'{top_class} ({top_confidence:.2f})')
        axes[i].axis('off')

    plt.tight_layout()
    plt.show()

#image_recognition('images/Untitled-design-71.png')
batch_recognition()
