"""
This script is indeed to be used on raspberry pi only.
It's for testing a pi camera
"""
from picamera2 import Picamera2, Preview
import time

# Create a Picamera2 object
picam2 = Picamera2()

# Set the resolution (e.g., 1920x1080 for HD video)
config = picam2.create_preview_configuration(main={"size": (1920, 1080)})
picam2.configure(config)

# Start the camera preview using Qt OpenGL
picam2.start_preview(Preview.QTGL)

# Start the camera
picam2.start()

# Preview the camera feed for 20 seconds
print("Camera preview started... Press Ctrl+C to exit early.")
time.sleep(20)

# Stop the camera
picam2.stop()
print("Camera preview stopped.")
