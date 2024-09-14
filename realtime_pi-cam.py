import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import json
import time
from picamera2 import Picamera2, Preview

# Load the TFLite model and allocate tensors
interpreter = tflite.Interpreter(model_path="fine_tuned_model_4.tflite")
interpreter.allocate_tensors()

# Get input and output tensor details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load class indices
with open('class_indices.json', 'r') as f:
    class_indices = json.load(f)
class_labels = list(class_indices.keys())

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

# Function to predict top-3 classes for a frame using TFLite interpreter
def predict_top3_classes(frame):
    processed_frame = preprocess_frame(frame)

    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], processed_frame)

    # Run inference
    interpreter.invoke()

    # Get predictions from output tensor
    predictions = interpreter.get_tensor(output_details[0]['index'])

    # Get top-3 predictions
    top_indices = np.argsort(predictions[0])[-3:][::-1]
    top_classes = [class_labels[i] for i in top_indices]
    top_confidences = [predictions[0][i] for i in top_indices]
    return list(zip(top_classes, top_confidences))

# Function to draw top-3 predictions on the frame
def draw_predictions_on_frame(frame, predictions):
    for i, (label, confidence) in enumerate(predictions):
        cv2.putText(frame, f'{label} ({confidence:.2f})', (10, 30 + 30 * i),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# Function to capture and display real-time detection using Pi Camera
def real_time_detection(process_every_n_frames=2):
    # Create a Picamera2 object
    picam2 = Picamera2()

    # Set the resolution (e.g., 1920x1080 for HD video)
    config = picam2.create_preview_configuration(main={"size": (1920, 1080)})
    picam2.configure(config)

    # Start the camera
    picam2.start()

    start_time = time.time()
    frame_count = 0

    while True:
        # Capture frame-by-frame from Pi Camera
        frame = picam2.capture_array()

        frame_count += 1

        if frame_count % process_every_n_frames == 0:
            predictions = predict_top3_classes(frame)
            draw_predictions_on_frame(frame, predictions)

        draw_fps(frame, start_time, frame_count)

        # Display the frame using OpenCV
        cv2.imshow('Real-Time Fruit Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Stop the camera and close OpenCV windows
    picam2.stop()
    cv2.destroyAllWindows()

# Run the real-time detection
real_time_detection()
