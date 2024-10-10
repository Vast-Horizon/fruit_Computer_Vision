import time
import requests
import math
import random

TOKEN = "BBUS-zFNs6h6YSIb6EO1Bbk676Ab5thPCH6"  # Put your TOKEN here
DEVICE_LABEL = "cybercart"  # Put your device label here
recognition1_label = 'predict1'
recognition2_label = 'predict2'
recognition3_label = 'predict3'
detecting_label = 'detecting'
selection_label = 'selection'
re_detect_label = 're_detect'
weight_label = 'weight'

selection_state = 0
re_detect_state = 0

def get_request(device, variable):
    try:
        url = "http://industrial.api.ubidots.com/"
        url = url + \
            "api/v1.6/devices/{0}/{1}/".format(device, variable)
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        req = requests.get(url=url, headers=headers)
        return req.json()['last_value']['value']
    except:
        pass

def build_payload(variable_1, variable_2, variable_3):

    predict1 = 'tomato'
    random_weights = random.randint(1, 10)
    payload = {variable_1: {"value": 99, "context": {"predict1": predict1.capitalize()}},
               variable_2: {"value": random_weights}, variable_3:{"value": 1}
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
        recognition1_label, weight_label, detecting_label)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")


if __name__ == '__main__':
    while (True):
        main()
        selection_state = get_request(DEVICE_LABEL, selection_label)
        if selection_state == 1:
            re_detect_state = 0
        if re_detect_state == 1:
            selection_state = 0
        main()
        time.sleep(5)
