'''
This is a temporary main.py for running RFID class
'''
from RFID_class_old import RFIDReader
import time


def main():
    # Initialize the RFID reader
    rfid_reader = RFIDReader()

    # Start the RFID reader in a separate thread
    rfid_reader.start()

    try:
        while True:
            # Get the latest tag details
            tag_info = rfid_reader.get()
            if tag_info:
                print(f"Latest Tag: UID = {tag_info['uid']}, "
                      f"Name = {tag_info['name']}, "
                      f"Price = {tag_info['price']}")
            time.sleep(1)  # Check for new tags every second
    except KeyboardInterrupt:
        print("Stopping RFID Reader...")
        rfid_reader.stop()


if __name__ == "__main__":
    main()
