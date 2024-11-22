#!/usr/bin/env python
# -*- coding: utf8 -*-

import MFRC522
import signal
import os
import RPi.GPIO as GPIO

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("\nCtrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

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

# Initialize two RFID readers
def initialize_readers():
    reader1 = MFRC522.MFRC522(cs=0)  # Reader 1 with CS pin GPIO 8 (default SPI bus 0)
    reader2 = MFRC522.MFRC522(cs=1)  # Reader 2 with CS pin GPIO 7 (SPI bus 1)
    return reader1, reader2

def main():
    global continue_reading
    data = load_data()
    reader1, reader2 = initialize_readers()

    print("Waiting to scan a tag...")

    while continue_reading:
        for reader in (reader1, reader2):
            # Scan for cards
            (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)

            # If a card is found
            if status == reader.MI_OK:
                print("\nCard detected")

                # Get the UID of the card
                (status, uid) = reader.MFRC522_Anticoll()

                if status == reader.MI_OK:
                    # Convert UID to a readable string
                    uid_str = ",".join([str(x) for x in uid])
                    print(f"Card UID: {uid_str}")

                    # Display item details for the scanned UID
                    display_item(uid_str, data)

                    # Wait for user input before scanning again
                    input("\nPress Enter to continue...\n")

if __name__ == "__main__":
    main()
