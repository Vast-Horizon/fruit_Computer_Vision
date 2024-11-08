#!/usr/bin/env python
# -*- coding: utf8 -*-

import MFRC522
import signal
import os

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Path for the text file
file_path = "rfid_data.txt"

# Read the file into a dictionary
def load_data():
    data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for i in range(0, len(lines), 4):
                uid = lines[i].strip().split(": ")[1]
                item_name = lines[i + 1].strip().split(": ")[1]
                item_price = float(lines[i + 2].strip().split(": ")[1])
                data[uid] = (item_name, item_price)
    return data

# Function to display item details
def display_item(uid, data):
    if uid in data:
        item_name, item_price = data[uid]
        print(f"Item Name: {item_name}")
        print(f"Item Price: ${item_price:.2f}")
    else:
        print(f"No data found for UID: {uid}")

def main():
    global continue_reading
    data = load_data()

    while continue_reading:
        print("Waiting to scan a tag...")
        
        # Scan for cards    
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print("Card detected")

            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            if status == MIFAREReader.MI_OK:
                # Convert UID to a readable string
                uid_str = ",".join([str(x) for x in uid])
                print(f"Card UID: {uid_str}")

                # Display item details for the scanned UID
                display_item(uid_str, data)

                # Wait for user to press Enter before scanning again
                input("\nPress Enter to scan another tag...\n")

if __name__ == "__main__":
    main()
