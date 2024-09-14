from picamera2 import Picamera2
import time

# Create a Picamera2 object
picam2 = Picamera2()

# Configure the camera to use default preview settings
picam2.preview_configuration()

# Start the camera
picam2.start()

# Preview the camera feed for 10 seconds
print("Camera preview started... Press Ctrl+C to exit early.")
time.sleep(10)

# Stop the camera
picam2.stop()
print("Camera preview stopped.")
