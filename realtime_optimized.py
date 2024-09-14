'''
Frame Skipping: The script processes every nth frame to reduce the processing load.
Top-3 Predictions: It shows the top 3 predictions with confidence scores.
FPS Display: The frames per second (FPS) are calculated and displayed on the video feed.
'''
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import json
import time

# Load the fine-tuned model and class indices
model = load_model('fine_tuned_model_4.h5')

with open('class_indices.json', 'r') as f:
    class_indices = json.load(f)
class_labels = list(class_indices.keys())

# Function to list available cameras
def list_available_cameras(max_cameras=2):
    available_cameras = []
    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras

# Function to preprocess the frame for the model
def preprocess_frame(frame, target_size=(224, 224)):
    img = cv2.resize(frame, target_size)  # Resize the frame to the target size
    img_array = np.expand_dims(img, axis=0)  # Add batch dimension
    img_array = img_array.astype('float32') / 255.0  # Rescale to [0, 1]
    return img_array

# Function to calculate and display FPS on the frame
def draw_fps(frame, start_time, num_frames):
    fps = num_frames / (time.time() - start_time)
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Function to predict top-3 classes for a frame
def predict_top3_classes(frame):
    processed_frame = preprocess_frame(frame)
    predictions = model.predict(processed_frame)
    top_indices = np.argsort(predictions[0])[-3:][::-1]
    top_classes = [class_labels[i] for i in top_indices]
    top_confidences = [predictions[0][i] for i in top_indices]
    return list(zip(top_classes, top_confidences))

# Function to draw top-3 predictions on the frame
def draw_predictions_on_frame(frame, predictions):
    for i, (label, confidence) in enumerate(predictions):
        cv2.putText(frame, f'{label} ({confidence:.2f})', (10, 30 + 30 * i),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# Function to capture and display real-time detection
def real_time_detection(process_every_n_frames=2):
    cam_index_list = list_available_cameras()
    cap = cv2.VideoCapture(cam_index_list[0])

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    start_time = time.time()
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame")
            break

        frame_count += 1

        if frame_count % process_every_n_frames == 0:
            predictions = predict_top3_classes(frame)
            draw_predictions_on_frame(frame, predictions)

        draw_fps(frame, start_time, frame_count)
        cv2.imshow('Real-Time Fruit Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Run the real-time detection
real_time_detection()
