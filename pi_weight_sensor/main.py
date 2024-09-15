import threading
from predict_class import Recognition
from weight_class import Weighting
import time

def main():
    # Initialize the classes
    recognition = Recognition()
    weighting = Weighting(calibration_factor=0.00011765484757443882)

    # Create threads for both processes
    recognition_thread = threading.Thread(target=recognition.start_recognition)
    weighting_thread = threading.Thread(target=weighting.start)

    # Start both threads
    recognition_thread.start()
    weighting_thread.start()

    try:
        while True:
            time.sleep(0.1)  # Keep the main thread running
    except KeyboardInterrupt:
        print("Stopping both processes...")
        recognition.stop()
        weighting.stop()

        # Wait for both threads to finish
        recognition_thread.join()
        weighting_thread.join()
        print("Both processes stopped.")

if __name__ == "__main__":
    main()
