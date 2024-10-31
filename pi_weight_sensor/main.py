"""
main function prompts the user to start recognition, runs both the recognition and weight sensing for 1 sec
You can also use main_continuous function to run forever until KeyboardInterrupt
"""

import threading
from predict_class import Recognition
from weight_class import Weighting
import time
from ubidots_client import UbidotsClient

TOKEN = "BBUS-zFNs6h6YSIb6EO1Bbk676Ab5thPCH6"
DEVICE_LABEL = "cybercart"
client = UbidotsClient(token=TOKEN, device_label=DEVICE_LABEL)

payload_dict = client.get_default_payload()

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
    #recognition = Recognition()
    weighting = Weighting(calibration_factor=0.00011765484757443882)

    # Enable simulation modes for testing
    weighting.testing_only(enable_simulation=False)
    #recognition.enable_simulation(enable_simulation=False)

    input("Start Recognition? (Hit Enter to start)")
    n = 1  # Default duration (in seconds)

    # Create threads for both processes
    #recognition_thread = threading.Thread(target=recognition.start_recognition)
    weighting_thread = threading.Thread(target=weighting.start)
    stop_event = threading.Event()

    # Start both threads
    #recognition_thread.start()
    weighting_thread.start()

    try:
        # Continuously fetch the weight reading until the Enter key is pressed again
        while not stop_event.is_set():
            current_weight = weighting.get_weight()
            print(f"Current Weight: {current_weight}g")

            payload_dict = {'weight': current_weight}
            print(payload_dict)
            client.send_data(payload_dict)  # Send to Ubidots dashboard
            time.sleep(0.2)

            # Non-blocking check for Enter key press to stop
            if input("Press Enter to stop:\n") == "":
                stop_event.set()

    except KeyboardInterrupt:
        stop_event.set()  # Ensure the program stops on interrupt


    # for _ in range(n * 5):  # Runs 1*5 times because 1s has 5 0.2s
    #     # top_prediction = recognition.get_top_prediction()
    #     # if top_prediction:
    #     #     print(f"Top Prediction: {top_prediction[0]}") #not working yet in simulation mode
    #
    #     if current_weight > 0.2:
    #         pass #tigger the recognition_thread
    #     time.sleep(0.2)  # Same delay as in Weighting class

    # time.sleep(n)
    print("Stopping recognition and weighting...")
    #recognition.stop()
    weighting.stop()

    # Wait for both threads to finish
    #recognition_thread.join()
    weighting_thread.join()

    print("Program ended.")

if __name__ == "__main__":
    #main_continuous()
    main()
