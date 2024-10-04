import time
import requests
import math
import random

TOKEN = "BBUS-zFNs6h6YSIb6EO1Bbk676Ab5thPCH6"  # Put your TOKEN here
DEVICE_LABEL = "cybercart"  # Put your device label here
VARIABLE_LABEL_1 = "price"  # Put your first variable label here
VARIABLE_LABEL_2 = "weight"  # Put your second variable label here
VARIABLE_LABEL_3 = "predict1"  # Put your second variable label here
recognition1_label = 'predict1'
recognition2_label = 'predict2'
recognition3_label = 'predict3'
rfidcheck_label = 'rfidchecked'
cvcheck_label = 'cvchecked'

def build_payload(variable_1, variable_2, variable_3):
    # Creates two random values for sending data
    # value_1 = random.randint(10, 50)
    # value_2 = random.randint(0, 10)

    predict1 = 'tomato'
    predict2 = 'banana'
    predict3 = 'apple'

    payload = {variable_1: {"value": 99, "context": {"predict1": predict1.capitalize()}},
               variable_2: {"value": 1}, variable_3:{"value": 1}
               }

    return payload


def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    payload = build_payload(
        recognition1_label, rfidcheck_label, cvcheck_label)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")


if __name__ == '__main__':
    while (True):
        main()
        time.sleep(5)