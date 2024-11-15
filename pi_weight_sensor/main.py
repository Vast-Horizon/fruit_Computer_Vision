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
    recognition = Recognition()
    weighting = Weighting(calibration_factor=0.00011765484757443882)

    # Enable simulation modes for testing
    weighting.testing_only(enable_simulation=True)
    recognition.enable_simulation(enable_simulation=True)

    input("Start Recognition? (Hit Enter to start)")
    fruits_list = []
    total_price = 0
    # Create threads for both processes
    recognition_thread = threading.Thread(target=recognition.start_recognition)
    weighting_thread = threading.Thread(target=weighting.start)
    stop_event = threading.Event()

    # Start both threads
    recognition_thread.start()
    weighting_thread.start()

    try:
        while not stop_event.is_set():
            # Continuously fetch the weight reading until Keyboard Interrupt
            current_weight = weighting.get_weight()
            pounds = current_weight / 453.592
            print(f"Current Weight: {current_weight}g")
            payload_dict['weight'] = pounds
            print(payload_dict)

            # Continuously fetch the top prediction until Keyboard Interrupt
            top_prediction = recognition.get_top_prediction()
            if top_prediction:
                print(f"Current Top Prediction: {top_prediction[0]}")
                payload_dict['predict1'] = top_prediction[0]
                fruits_list.append(top_prediction[0])
                results_string = ", ".join(fruits_list)
                payload_dict['results'] = results_string

            # Continuously fetch the price until Keyboard Interrupt
            price = 2 * pounds # Assuming the items are all $2 per lb.
            payload_dict['price'] = price
            total_price += price
            payload_dict['total'] = total_price
            client.send_data(payload_dict)  # Send to Ubidots dashboard
            time.sleep(0.2)

    except KeyboardInterrupt:
        stop_event.set()

    # try:
    #     # Continuously fetch the top prediction until Keyboard Interrupt
    #     while not stop_event.is_set():
    #         top_prediction = recognition.get_top_prediction()
    #         if top_prediction:
    #             print(f"Current Top Prediction: {top_prediction[0]}")
    #             payload_dict['predict1'] = top_prediction[0]
    #             client.send_data(payload_dict)
    #         # if current_weight > 0.2:
    #         #     pass #tigger the recognition_thread
    #         time.sleep(0.2)
    # except KeyboardInterrupt:
    #     stop_event.set()

    print("Stopping recognition and weighting...")
    recognition.stop()
    weighting.stop()

    # Wait for both threads to finish
    recognition_thread.join()
    weighting_thread.join()

    print("Program ended.")


def main():
    recognition = Recognition()
    weighting = Weighting(calibration_factor=0.00011765484757443882)

    # Enable simulation modes for testing
    weight_sim = False
    recog_sim = True
    weighting.testing_only(enable_simulation=weight_sim)
    recognition.enable_simulation(enable_simulation=recog_sim)

    input("Start Recognition? (Hit Enter to start)")
    fruits_list = []
    total_price = 0
    # Create threads for both processes
    recognition_thread = threading.Thread(target=recognition.start_recognition)
    weighting_thread = threading.Thread(target=weighting.start)
    stop_event = threading.Event()

    # Start both threads
    recognition_thread.start()
    weighting_thread.start()

    # Initialize state variables
    item_detected = False
    if weight_sim:
        weight_threshold = 7
    else:
        weight_threshold = 0.2

    try:
        while not stop_event.is_set():
            # Continuously fetch the weight reading
            current_weight = weighting.get_weight()
            pounds = current_weight / 453.592
            print(f"Current Weight: {current_weight}g")
            payload_dict['weight'] = pounds
            client.send_data(payload_dict)

            # Detect when the weight goes above 0.2g for the first time
            if current_weight > weight_threshold and not item_detected:
                # Trigger camera recognition
                top_prediction = recognition.get_top_prediction()
                if top_prediction:
                    print(f"Current Top Prediction: {top_prediction[0]}")
                    payload_dict['predict1'] = top_prediction[0]
                    price = 2 * pounds  # Assuming the items are all $2 per lb.
                    payload_dict['price'] = price
                    client.send_data(payload_dict)

                    # Wait for 5 seconds for user confirmation
                    start_time = time.time()
                    while time.time() - start_time < 5:
                        select_button = client.get_request("selection")
                        if select_button == 1:
                            # User confirmed the item
                            fruits_list.append(top_prediction[0])
                            results_string = ", ".join(fruits_list)
                            payload_dict['results'] = results_string
                            payload_dict['selection'] = 0
                            total_price += price
                            payload_dict['total'] = total_price
                            client.send_data(payload_dict)
                            print("Item confirmed.")
                            break
                        time.sleep(0.2)

                    # If not confirmed within 5 seconds, clear prediction and price
                    if select_button == 0:
                        print("Item not confirmed, clearing...")
                        payload_dict['predict1'] = ""
                        payload_dict['price'] = 0
                        client.send_data(payload_dict)

                    # Mark item as detected to avoid re-triggering recognition
                    item_detected = True

            # Reset detection if weight is removed (goes below threshold)
            if current_weight < weight_threshold:
                item_detected = False

            time.sleep(0.2)

    except KeyboardInterrupt:
        stop_event.set()

    print("Stopping recognition and weighting...")
    recognition.stop()
    weighting.stop()

    # Wait for both threads to finish
    recognition_thread.join()
    weighting_thread.join()

    print("Program ended.")

if __name__ == "__main__":
    #main_continuous()
    main()
