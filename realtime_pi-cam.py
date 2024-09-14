from picamera2 import Picamera2
import numpy as np
import tflite_runtime.interpreter as tflite
import json
import time
import cv2

# Load TFLite model and allocate tensors.
interpreter = tflite.Interpreter(model_path="fine_tuned_model_4.tflite")
interpreter.allocate_tensors()

# Get input details to check input shape
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']  # Example: [1, 224, 224, 3] or [224, 224, 3]

# Load the class indices
with open('class_indices.json', 'r') as f:
    class_indices = json.load(f)
class_labels = list(class_indices.keys())


# Function to preprocess the frame for the model
def preprocess_frame(frame, target_size=(224, 224)):
    img = cv2.resize(frame, target_size)  # Resize the frame to the target size
    img = img.astype('float32') / 255.0  # Normalize to [0, 1]

    if len(input_shape) == 3:  # If model expects [height, width, channels]
        return img  # No batch dimension needed
    elif len(input_shape) == 4:  # If model expects [1, height, width, channels]
        img = np.expand_dims(img, axis=0)  # Add batch dimension
        return img


# Function to predict top-3 classes for a frame
def predict_top3_classes(frame):
    processed_frame = preprocess_frame(frame)

    # Remove batch dimension if present (ensure 3D input)
    if len(processed_frame.shape) == 4 and len(input_shape) == 3:
        processed_frame = processed_frame[0]

    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], processed_frame)

    # Invoke the interpreter
    interpreter.invoke()

    # Get the output tensor
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]

    # Get top-3 predictions
    top_indices = np.argsort(predictions)[-3:][::-1]
    top_classes = [class_labels[i] for i in top_indices]
    top_confidences = [predictions[i] for i in top_indices]
    return list(zip(top_classes, top_confidences))


# Function to log the top-3 predictions
def log_predictions(frame_count, predictions):
    print(f"Frame {frame_count}, Top 3 Predictions:")
    for i, (label, confidence) in enumerate(predictions):
        print(f"{i + 1}: {label} ({confidence:.2f})")
    print()  # Add a blank line for better readability


# Function to run real-time detection and print top-3 predictions
def real_time_detection(process_every_n_frames=2):
    # Create a Picamera2 object
    picam2 = Picamera2()

    # Set the resolution (e.g., 1920x1080 for HD video)
    config = picam2.create_preview_configuration(main={"size": (1920, 1080)})
    picam2.configure(config)

    # Start the camera
    picam2.start()

    frame_count = 0

    try:
        while True:
            # Capture frame-by-frame from Pi Camera
            frame = picam2.capture_array()

            frame_count += 1

            if frame_count % process_every_n_frames == 0:
                # Predict top-3 classes for the current frame
                predictions = predict_top3_classes(frame)

                # Log the predictions to the console
                log_predictions(frame_count, predictions)

            # To stop the loop, press Ctrl+C

    except KeyboardInterrupt:
        # Stop the camera when interrupted
        picam2.stop()
        print("Real-time detection stopped.")


# Run the real-time detection
real_time_detection()
