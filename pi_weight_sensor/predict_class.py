import numpy as np
import tflite_runtime.interpreter as tflite
import json
import time
import cv2
from picamera2 import Picamera2


class Recognition:
    def __init__(self, model_path="fine_tuned_model_4.tflite", class_indices_path="class_indices.json",
                 resolution=(1920, 1080), process_every_n_frames=4):
        # Load TFLite model and allocate tensors.
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_shape = self.input_details[0]['shape']

        # Load class labels
        with open(class_indices_path, 'r') as f:
            self.class_indices = json.load(f)
        self.class_labels = list(self.class_indices.keys())

        # Set camera configuration
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(main={"size": resolution})
        self.picam2.configure(config)

        self.frame_count = 0
        self.process_every_n_frames = process_every_n_frames
        self.running = True  # Flag to control the loop

    def preprocess_frame(self, frame, target_size=(224, 224)):
        img = cv2.resize(frame, target_size)  # Resize the frame to the target size
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)  # Convert to RGB if necessary
        img = img.astype('float32') / 255.0  # Normalize to [0, 1]

        # Add batch dimension if necessary
        if len(self.input_shape) == 4:
            img = np.expand_dims(img, axis=0)

        return img

    def predict_top3_classes(self, frame):
        processed_frame = self.preprocess_frame(frame)

        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], processed_frame)

        # Invoke the interpreter
        self.interpreter.invoke()

        # Get the output tensor
        predictions = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

        # Get top-3 predictions
        top_indices = np.argsort(predictions)[-3:][::-1]
        top_classes = [self.class_labels[i] for i in top_indices]
        top_confidences = [predictions[i] for i in top_indices]

        return list(zip(top_classes, top_confidences))

    def log_predictions(self, predictions):
        for i, (label, confidence) in enumerate(predictions):
            print(f"{i + 1}: {label} ({confidence:.2f})")
        print()

    def start_recognition(self):
        # Start the camera
        self.picam2.start()
        try:
            while self.running:
                # Capture frame-by-frame from Pi Camera
                frame = self.picam2.capture_array()
                self.frame_count += 1

                if self.frame_count % self.process_every_n_frames == 0:
                    # Predict top-3 classes for the current frame
                    predictions = self.predict_top3_classes(frame)

                    # Log the predictions to the console
                    self.log_predictions(predictions)

        except KeyboardInterrupt:
            pass
        finally:
            # Stop the camera and clean up
            self.picam2.stop()
            print("Real-time detection stopped.")

    def stop(self):
        self.running = False
