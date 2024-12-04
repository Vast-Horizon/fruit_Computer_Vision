"""
main function prompts the user to start recognition, runs both the recognition and weight sensing for 1 sec
You can also use main_continuous function to run forever until KeyboardInterrupt
"""

import threading
from predict_class import Recognition
from weight_class import Weighting
from RFID_class import RFIDReader
import time
from ubidots_client import UbidotsClient


TOKEN = "BBUS-zFNs6h6YSIb6EO1Bbk676Ab5thPCH6"
DEVICE_LABEL = "cybercart"
client = UbidotsClient(token=TOKEN, device_label=DEVICE_LABEL)

#payload_dict = client.get_default_payload()



def main_continuous():
    '''
    This main function is for development purposes, not the real main function
    '''
    recognition = Recognition()
    weighting = Weighting(calibration_factor=0.00011765484757443882)

    # Enable simulation modes for testing
    weighting.testing_only(enable_simulation=True)
    recognition.enable_simulation(enable_simulation=True)

    input("Start Recognition? (Hit Enter to start)")
    payload_dict = client.get_default_payload()
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

    print("Stopping recognition and weighting...")
    recognition.stop()
    weighting.stop()

    # Wait for both threads to finish
    recognition_thread.join()
    weighting_thread.join()

    print("Program ended.")





def main_no_rfid():
    recognition = Recognition()
    weighting = Weighting(calibration_factor=0.00011765484757443882)
    rfid_reader = RFIDReader()

    # Enable simulation modes for testing
    weight_sim = False
    recog_sim = False
    weighting.testing_only(enable_simulation=weight_sim)
    recognition.enable_simulation(enable_simulation=recog_sim)

    payload_dict = client.get_default_payload()
    fruits_list = []
    total_price = 0
    weight_threshold = 7 if weight_sim else 20

    # Variable to control dashboard data sending
    active = False

    # Initialize threads and stop_event
    recognition_thread = threading.Thread(target=recognition.start_recognition)
    weighting_thread = threading.Thread(target=weighting.start)
    rfid_thread = threading.Thread(target=rfid_reader.start)

    stop_event = threading.Event()

    # Start threads
    recognition_thread.start()
    weighting_thread.start()
    rfid_thread.start()

    # Variable to manage item detection state
    item_detected = False

    try:
        while not stop_event.is_set():
            # Check reset button status every 0.5 seconds
            reset_button = client.get_request("reset")
            if reset_button == 1:
                print("Reset button pressed. Activating data sending.")
                payload_dict['reset'] = 0
                fruits_list = []
                total_price = 0
                payload_dict = client.get_default_payload()
                client.send_data(payload_dict)
                active = True

            # Check payment button status
            pay_button = client.get_request("payment")
            if pay_button == 1 and active:
                print("Payment initiated. Sending QR code.")
                payload_dict['payment'] = 0
                #payload_dict['qrcode'] = "https://i.ibb.co/StXdGRp/qrcode.png" #larger qr code
                payload_dict['qrcode'] = "https://i.ibb.co/9WrDXgh/qrcode.png"
                client.send_data(payload_dict)
                print("Data sending paused. Waiting for reset button.")
                active = False  # Pause data sending

            # Continue thread operations but only send data if active
            if active:
                current_weight = weighting.get_weight()
                pounds = current_weight / 453.592
                print(f"Current Weight: {current_weight}g")
                payload_dict['weight'] = pounds
                client.send_data(payload_dict)

                # Detect when the weight goes above threshold for the first time
                if current_weight > weight_threshold and not item_detected:
                    latest_rfid = rfid_reader.get()
                    if latest_rfid:
                        print(f"Latest RFID result: {latest_rfid}")

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

                        item_detected = True

                # Reset detection if weight is removed (goes below threshold)
                if current_weight < weight_threshold:
                    item_detected = False
                    payload_dict['predict1'] = ""
                    payload_dict['price'] = 0
                    client.send_data(payload_dict)

            time.sleep(1)  # Main loop interval

    except KeyboardInterrupt:
        stop_event.set()

    print("Stopping recognition and weighting...")
    recognition.stop()
    weighting.stop()
    rfid_reader.stop()

    # Wait for both threads to finish
    recognition_thread.join()
    weighting_thread.join()
    rfid_thread.join()

    print("Program ended.")

def main():
    recognition = Recognition()
    weighting = Weighting(calibration_factor=0.00011765484757443882)
    rfid_reader = RFIDReader()

    # Enable simulation modes for testing
    weight_sim = False
    recog_sim = False
    weighting.testing_only(enable_simulation=weight_sim)
    recognition.enable_simulation(enable_simulation=recog_sim)

    payload_dict = client.get_default_payload()
    fruits_list = []
    total_price = 0
    weight_threshold = 7 if weight_sim else 20

    # Variable to control dashboard data sending
    active = False

    # Initialize threads and stop_event
    recognition_thread = threading.Thread(target=recognition.start_recognition)
    weighting_thread = threading.Thread(target=weighting.start)
    rfid_thread = threading.Thread(target=rfid_reader.start)

    stop_event = threading.Event()

    # Start threads
    recognition_thread.start()
    weighting_thread.start()
    rfid_thread.start()

    # Variable to manage item detection state
    item_detected = False

    try:
        while not stop_event.is_set():
            # Check reset button status every 0.5 seconds
            reset_button = client.get_request("reset")
            if reset_button == 1:
                print("Reset button pressed. Activating data sending.")
                payload_dict['reset'] = 0
                fruits_list = []
                total_price = 0
                payload_dict = client.get_default_payload()
                client.send_data(payload_dict)
                active = True

            # Check payment button status
            pay_button = client.get_request("payment")
            if pay_button == 1 and active:
                print("Payment initiated. Sending QR code.")
                payload_dict['payment'] = 0
                #payload_dict['qrcode'] = "https://i.ibb.co/StXdGRp/qrcode.png" #larger qr code
                payload_dict['qrcode'] = "https://i.ibb.co/9WrDXgh/qrcode.png"
                client.send_data(payload_dict)
                print("Data sending paused. Waiting for reset button.")
                active = False  # Pause data sending

            # Continue thread operations but only send data if active
            if active:
                current_weight = weighting.get_weight()
                pounds = current_weight / 453.592
                print(f"Current Weight: {current_weight}g")
                payload_dict['weight'] = pounds
                price = 2 * pounds
                client.send_data(payload_dict)

                # Detect when the weight goes above threshold for the first time
                if current_weight > weight_threshold and not item_detected:
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

                    item_detected = True

                # Reset detection if weight is removed (goes below threshold)
                if current_weight < weight_threshold:
                    item_detected = False
                    payload_dict['predict1'] = ""
                    payload_dict['price'] = 0
                    client.send_data(payload_dict)

            time.sleep(1)  # Main loop interval

    except KeyboardInterrupt:
        stop_event.set()

    print("Stopping recognition and weighting...")
    recognition.stop()
    weighting.stop()
    rfid_reader.stop()

    # Wait for both threads to finish
    recognition_thread.join()
    weighting_thread.join()
    rfid_thread.join()

    print("Program ended.")
if __name__ == "__main__":
    main()
