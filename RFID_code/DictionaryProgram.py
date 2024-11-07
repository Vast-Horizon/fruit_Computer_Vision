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

# Function to write data to a file
def save_to_file(uid, item_name, item_price):
    with open(file_path, 'a') as file:
        file.write(f"UID: {uid}\n")
        file.write(f"Item Name: {item_name}\n")
        file.write(f"Item Price: {item_price:.2f}\n")
        file.write("-" * 30 + "\n")
    print(f"Data saved for UID {uid}")

def main():
    global continue_reading

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

                # Save to file
                save_to_file(uid_str, item_name, item_price)

                # Reset the reader for the next scan
                print("Ready to scan the next card...\n")

if __name__ == "__main__":
    main()
