import threading
from recognition_module import Recognition  # Assuming the Recognition class is in recognition_module.py
from weighting_module import Weighting  # Assuming the Weighting class is in weighting_module.py

# Initialize instances of the classes
recognition = Recognition()
weighting = Weighting(calibration_factor=0.00011765484757443882)

# Create threads for both classes
recognition_thread = threading.Thread(target=recognition.start_recognition)
weighting_thread = threading.Thread(target=weighting.start)

# Start both threads
recognition_thread.start()
weighting_thread.start()

# Wait for both threads to finish (optional, since they run indefinitely)
recognition_thread.join()
weighting_thread.join()
