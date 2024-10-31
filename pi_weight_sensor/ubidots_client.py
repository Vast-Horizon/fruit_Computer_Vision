import time
import requests
import random

class UbidotsClient:
    def __init__(self, token, device_label):
        self.token = token
        self.device_label = device_label
        self.headers = {"X-Auth-Token": self.token, "Content-Type": "application/json"}
        self.payload_dict_default = {
        "predict1": "tomato",
        "detecting": 0,
        "selection": 0,
        "re_detect": 0,
        "weight": 5,
        "price": 0,
        "total": 0,
        "payment": 0,
        "results": "tomato, apple"
        }

    def get_default_payload(self):
        return self.payload_dict_default

    def get_request(self, variable):
        """Fetch the last value of a specified variable from Ubidots."""
        try:
            url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{self.device_label}/{variable}/"
            req = requests.get(url=url, headers=self.headers)
            print("get_request req:", req.json())
            return req.json()['last_value']['value']
        except Exception as e:
            print(f"Error in get_request: {e}")
            return None

    def format_payload(self, payload_dict):
        """Build the payload for sending to Ubidots."""

        payload = {
            'predict1': {"value": 99, "context": {"predict1": payload_dict['predict1'].capitalize()}},
            'results': {"value": 99, "context": {"results": payload_dict['results']}},
            'weight': {"value": payload_dict['weight']},
            'selection': {"value": payload_dict['selection']},
            'detecting': {"value": payload_dict['detecting']},
            'price': {"value": payload_dict['price']},
            'total': {"value": payload_dict['total']},
            'payment': {"value": payload_dict['payment']},
        }

        return payload

    def post_request(self, payload):
        """Send the payload to Ubidots."""
        url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{self.device_label}"
        status = 400
        attempts = 0
        while status >= 400 and attempts <= 5:
            req = requests.post(url=url, headers=self.headers, json=payload)
            status = req.status_code
            attempts += 1
            time.sleep(1)

        # Log and handle request results
        # print(req.status_code, req.json())
        if status >= 400:
            print("[ERROR] Could not send data after 5 attempts, please check your token and connection")
            return False

        print("[INFO] request made successfully, device updated")
        return True

    def send_data(self, payload_dict):
        """Build the payload and send data to Ubidots."""
        payload = self.format_payload(payload_dict)
        print("[INFO] Attempting to send data")
        return self.post_request(payload)


# Example usage
if __name__ == '__main__':
    TOKEN = "BBUS-zFNs6h6YSIb6EO1Bbk676Ab5thPCH6"
    DEVICE_LABEL = "cybercart"

    client = UbidotsClient(token=TOKEN, device_label=DEVICE_LABEL)

    payload_dict = {
        "predict1": "tomato",
        "detecting": 0,
        "selection": 0,
        "re_detect": 0,
        "weight": 5,
        "price": 0,
        "total": 0,
        "payment": 0,
        "results": "tomato, apple"
    }
    fruits_list = []
    while True:
        # Random weight
        random_num = random.randint(1, 10)
        payload_dict['weight'] = random_num

        # Random fruits
        fruits = ["apple", "banana", "orange", "grape", "strawberry", "pineapple", "peas", "soy beans", "watermelon"]
        random_fruit = random.choice(fruits)
        fruits_list.append(random_fruit)
        results_string = ", ".join(fruits_list)
        payload_dict['results'] = results_string
        payload_dict["predict1"] = random_fruit

        # Send to Ubidots
        client.send_data(payload_dict)
        time.sleep(2)
