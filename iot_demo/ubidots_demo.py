from ubidots import ApiClient
import random
import time

# Replace with your Ubidots Token
UBIDOTS_TOKEN = "BBUS-zFNs6h6YSIb6EO1Bbk676Ab5thPCH6"

# Initialize the API client
api = ApiClient(token=UBIDOTS_TOKEN)

# Replace 'your-device-label' and 'your-variable-label' with your specific labels
device = api.get_device('cybercart')
temperature_variable = device.get_variable('numbers')

def send_data():
    # Simulate temperature data or use a sensor to get real data
    temperature = random.uniform(20.0, 30.0)
    print(f"Sending temperature: {temperature:.2f}")

    # Send the data to Ubidots
    temperature_variable.save_value({'value': temperature})

if __name__ == "__main__":
    while True:
        send_data()
        time.sleep(10)  # Send data every 10 seconds
