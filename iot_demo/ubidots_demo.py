"""
Send values to Ubidots.
Receive Values from Ubidots
"""

import time
import requests
import math
import random

TOKEN = "BBUS-zFNs6h6YSIb6EO1Bbk676Ab5thPCH6"
DEVICE_LABEL = "cybercart"
selection_state = 0
re_detect_state = 0



payload_dict = {
    "predict1": "tomato",
    "detecting": 0,
    "selection": 0,
    "re_detect": 0,
    "weight": 5,
    "price": 0,
    "total": 0,
    "payment": 0,
    "results": ["apple"]
}


def get_request(device, variable):
    try:
        url = "http://industrial.api.ubidots.com/"
        url = url + \
            "api/v1.6/devices/{0}/{1}/".format(device, variable)
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        req = requests.get(url=url, headers=headers)
        print("get_request req:", req.json())
        return req.json()['last_value']['value']
    except:
        pass

def build_payload(payload_dict):
    random_num = random.randint(1, 10)
    payload_dict['weight'] = random_num

    fruits = ["apple", "banana", "orange", "grape", "strawberry", "pineapple", "peas", "soy beans", "watermelon"]

    random_fruit = random.choice(fruits)
    payload_dict["results"].append(random_fruit)
    results_string = ", ".join(payload_dict["results"])

    payload_dict["predict1"] = random_fruit

    payload = {'predict1': {"value": 99, "context": {"predict1": payload_dict['predict1'].capitalize()}},
               'results': {"value": 99, "context": {"results": results_string}},
               'weight': {"value": payload_dict['weight']},
               'selection':{"value": payload_dict['selection']},
               'detecting': {"value": payload_dict['detecting']},
               'price': {"value": payload_dict['price']},
               'total': {"value": payload_dict['total']},
               'payment': {"value": payload_dict['payment']},
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

    payload = build_payload(payload_dict)
    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")



if __name__ == '__main__':

    while (True):
        main()
        # selection_state = get_request(DEVICE_LABEL, selection_label)
        time.sleep(5)
