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

# Ensure file exists
if not os.path.exists(file_path):
    open(file_path, 'w').close()

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

# Save data back to file
def save_all_data(data):
    with open(file_path, 'w') as file:
        for uid, (item_name, item_price) in data.items():
            file.write(f"UID: {uid}\n")
            file.write(f"Item Name: {item_name}\n")
            file.write(f"Item Price: {item_price:.2f}\n")
            file.write("-" * 30 + "\n")

# Function to save or update data
def save_or_update(uid, item_name, item_price, data):
    if uid in data:
        print(f"UID {uid} found. Updating item details.")
    else:
        print(f"UID {uid} not found. Adding new entry.")
    
    data[uid] = (item_name, item_price)
    save_all_data(data)
    print(f"Data saved for UID {uid}")

def main():
    global continue_reading
    data = load_data()

    while continue_reading:
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

                # Get user inputs for item details
                item_name = input("Enter Item Name: ")
                item_price = float(input("Enter Item Price: "))

                # Save or update the file
                save_or_update(uid_str, item_name, item_price, data)

                print("Ready to scan the next card...\n")

if __name__ == "__main__":
    main()
