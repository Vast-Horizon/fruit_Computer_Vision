"""
main function prompts the user to start recognition, runs both the recognition and weight sensing for 1 sec
You can also use main_continuous function to run forever until KeyboardInterrupt
"""

import threading
from predict_class import Recognition
from weight_class import Weighting
import time


def main_continuous():
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


def main():
    recognition = Recognition()
    weighting = Weighting(calibration_factor=0.00011765484757443882)

    input("Start Recognition? (Hit Enter to start)")
    n = 1  # Default duration (in seconds)

    # Create threads for both processes
    recognition_thread = threading.Thread(target=recognition.start_recognition)
    weighting_thread = threading.Thread(target=weighting.start)

    # Start both threads
    recognition_thread.start()
    weighting_thread.start()

    # Let the program run for 'n' seconds
    time.sleep(n)
    print("Stopping recognition and weighting...")
    recognition.stop()
    weighting.stop()

    # Wait for both threads to finish
    recognition_thread.join()
    weighting_thread.join()

    print("Program ended.")

if __name__ == "__main__":
    main()
