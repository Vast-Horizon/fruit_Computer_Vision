import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import json
import time

def list_available_cameras(max_cameras=2):
    available_cameras = []
    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras

# Load the fine-tuned model
model = load_model('fine_tuned_model_4.h5')

# Load the class indices
with open('class_indices.json', 'r') as f:
    class_indices = json.load(f)
class_labels = list(class_indices.keys())


# Function to preprocess the frame for the model
def preprocess_frame(frame, target_size=(224, 224)):
    img = cv2.resize(frame, target_size)  # Resize the frame to the target size
    img_array = np.expand_dims(img, axis=0)  # Add batch dimension
    img_array = img_array.astype('float32') / 255.0  # Rescale to [0, 1]
    return img_array


# Function to calculate and display FPS
def draw_fps(frame, start_time, num_frames):
    fps = num_frames / (time.time() - start_time)
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)


# Open the webcam
cam_index_list = list_available_cameras()
cap = cv2.VideoCapture(cam_index_list[0])

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Start capturing video
start_time = time.time()
frame_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to grab frame")
        break

    frame_count += 1

    # Preprocess the frame
    processed_frame = preprocess_frame(frame)

    # Make prediction
    predictions = model.predict(processed_frame)

    # Get the top 3 predictions
    top_indices = np.argsort(predictions[0])[-3:][::-1]
    top_classes = [class_labels[i] for i in top_indices]
    top_confidences = [predictions[0][i] for i in top_indices]

    # Display the top prediction on the frame
    label = f'{top_classes[0]} ({top_confidences[0]:.2f})'
    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the next 2 top predictions
    for i in range(1, 3):
        cv2.putText(frame, f'{top_classes[i]} ({top_confidences[i]:.2f})',
                    (10, 30 + 30 * (i + 1)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Display FPS on the frame
    draw_fps(frame, start_time, frame_count)

    # Display the frame
    cv2.imshow('Real-Time Fruit Detection', frame)

    # Press 'q' to exit the real-time detection
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
