import numpy as np
import json
import time
import random
import cv2

try:
    from picamera2 import Picamera2
    import tflite_runtime.interpreter as tflite
except ModuleNotFoundError:
    print('Recognition Class is Not in raspberry Pi environment')

class Recognition:
    def __init__(self, model_path="fine_tuned_model_4.tflite", class_indices_path="class_indices.json",
                 resolution=(1920, 1080), process_every_n_frames=4):
        self.simulation_mode = False  # For testing purposes

        try:
            # Load TFLite model and allocate tensors.
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()

            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.input_shape = self.input_details[0]['shape']
        except NameError:
            pass

        # Load class labels
        with open(class_indices_path, 'r') as f:
            self.class_indices = json.load(f)
        self.class_labels = list(self.class_indices.keys())

        try:
            # Set camera configuration
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(main={"size": resolution})
            self.picam2.configure(config)
            self.frame_count = 0
            self.process_every_n_frames = process_every_n_frames
        except NameError:
            pass

        self.running = True  # Flag to control the loop
        self.top_prediction = None  # Store top prediction



    def preprocess_frame(self, frame, target_size=(224, 224)):
        img = cv2.resize(frame, target_size)  # Resize the frame to the target size
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)  # Convert to RGB if necessary
        img = img.astype('float32') / 255.0  # Normalize to [0, 1]

        # Add batch dimension if necessary
        if len(self.input_shape) == 4:
            img = np.expand_dims(img, axis=0)

        return img

    def prpredict_top_class(self, frame):
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

    def get_top_prediction(self):
        """Returns the top prediction (class and confidence)."""
        if self.simulation_mode:
            try:
                self.simulate_recognition()
            except KeyboardInterrupt:
                print("Simulation stopped...")
        return self.top_prediction

    def start_recognition(self):
        if self.simulation_mode:
            try:
                self.simulate_recognition()
            except KeyboardInterrupt:
                print("Simulation stopped...")
        else:
            self.picam2.start()
            try:
                while self.running:
                    # Capture frame-by-frame from Pi Camera
                    frame = self.picam2.capture_array()
                    self.frame_count += 1

                    if self.frame_count % self.process_every_n_frames == 0:
                        # Predict top-3 classes for the current frame
                        predictions = self.prpredict_top_class(frame)

                        # Log the predictions to the console
                        #self.log_predictions(predictions)
                        self.top_prediction = predictions[0]

            except KeyboardInterrupt:
                pass
            finally:
                # Stop the camera and clean up
                self.picam2.stop()
                print("Real-time detection stopped.")

    def stop(self):
        self.running = False

    def simulate_recognition(self):
        """Simulates recognition by setting a random fruit as the top prediction."""
        fruits = ["apple", "banana", "orange", "strawberry", "grape", "pineapple", "mango"]
        # Randomly choose a fruit as the top prediction every 0.2 seconds
        random_fruit = random.choice(fruits)
        self.top_prediction = (random_fruit, random.uniform(0.8, 1.0))  # High confidence
        print(f"Simulated Top Prediction: {self.top_prediction[0]} ({self.top_prediction[1]:.2f})")
        #time.sleep(0.2)

    def enable_simulation(self, enable_simulation=True):
        """Enables or disables simulation mode."""
        self.simulation_mode = enable_simulation