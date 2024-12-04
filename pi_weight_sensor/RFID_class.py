import os
import time
import sys
import os

parent_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(parent_dir)
from RFID_code import MFRC522


class RFIDReader:
    def __init__(self, file_path="RFID_code/rfid_data.txt"):
        self.file_path = file_path
        self.data = self._load_data()
        self.mifare_reader = MFRC522.MFRC522()
        self.latest_tag = None
        self.running = False  # Flag to control the loop

    def _load_data(self):
        """Load data from the file into a dictionary."""
        data = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for i in range(0, len(lines), 4):
                    uid = lines[i].strip().split(": ")[1]
                    item_name = lines[i + 1].strip().split(": ")[1]
                    item_price = float(lines[i + 2].strip().split(": ")[1])
                    data[uid] = (item_name, item_price)
        return data

    def _display_item(self, uid):
        """Retrieve item details for a given UID."""
        if uid in self.data:
            item_name, item_price = self.data[uid]
            return {"uid": uid, "name": item_name, "price": item_price}
        else:
            return {"uid": uid, "name": "Unknown", "price": None}

    def start(self):
        """Start the RFID reader loop."""
        self.running = True
        try:
            while self.running:
                # Scan for cards
                (status, TagType) = self.mifare_reader.MFRC522_Request(self.mifare_reader.PICC_REQIDL)

                # If a card is found
                if status == self.mifare_reader.MI_OK:
                    # Get the UID of the card
                    (status, uid) = self.mifare_reader.MFRC522_Anticoll()
                    if status == self.mifare_reader.MI_OK:
                        # Convert UID to a readable string
                        uid_str = ",".join([str(x) for x in uid])
                        print(f"Card detected: UID = {uid_str}")

                        # Get the item details
                        self.latest_tag = self._display_item(uid_str)
                time.sleep(0.5)  # Slight delay to avoid continuous scanning
        except KeyboardInterrupt:
            pass
        finally:
            print("RFID Reader stopped.")

    def stop(self):
        """Stop the RFID reader."""
        self.running = False

    def get(self):
        """Retrieve the latest RFID tag data."""
        return self.latest_tag
