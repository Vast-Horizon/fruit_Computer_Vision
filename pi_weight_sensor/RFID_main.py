import threading
from RFID_class import RFIDReader
import time


def RFID_main():
    rfid_reader = RFIDReader()

    # Initialize the RFID thread
    rfid_thread = threading.Thread(target=rfid_reader.start)
    rfid_thread.start()

    try:
        print("RFID Reader is running. Press Ctrl+C to stop.")
        while True:
            # Continuously check for the latest tag
            latest_tag = rfid_reader.get()
            if latest_tag:
                print(f"Latest Tag: {latest_tag}")
            time.sleep(1)  # Adjust delay as needed

    except KeyboardInterrupt:
        print("\nStopping RFID Reader...")
        rfid_reader.stop()
        rfid_thread.join()
        print("RFID Reader stopped. Goodbye!")


if __name__ == "__main__":
    RFID_main()
