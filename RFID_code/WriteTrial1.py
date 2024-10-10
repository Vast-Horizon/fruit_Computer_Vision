#!/usr/bin/env python
# -*- coding: utf8 -*-

import MFRC522
import signal

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

# Function to write data to a block
def write_data_to_block(block, data):
    # Ensure data fits within 16 bytes
    if len(data) > 16:
        print("Data too long for the block. Max 16 bytes allowed.")
        return

    # Fill the remaining bytes with 0x00 to make data 16 bytes
    while len(data) < 16:
        data.append(0x00)
    
    MIFAREReader.MFRC522_Write(block, data)

# Main function
def main():
    global continue_reading

    # Ask the user for item information
    item_name = input("Enter the item name: ")
    price = input("Enter the item price: ")

    # Combine item name and price into a single string (max 16 characters)
    item_info = f"{item_name[:10]} ${price[:5]}"

    # Convert to a list of ASCII values
    data_to_write = [ord(x) for x in item_info]

    while continue_reading:
        # Scan for cards    
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print("Card detected")

            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:
                print("Writing data to the tag...")

                # This is the default key for authentication
                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                # Select the scanned tag
                MIFAREReader.MFRC522_SelectTag(uid)

                # Authenticate with block 8 (or any other block where you want to store data)
                status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

                # Check if authenticated
                if status == MIFAREReader.MI_OK:
                    print("Authenticated successfully.")
                    
                    # Write item information to block 8
                    write_data_to_block(8, data_to_write)

                    print(f"Item '{item_name}' with price '{price}' written to tag.")
                    
                    # Stop crypto and halt
                    MIFAREReader.MFRC522_StopCrypto1()
                    break
                else:
                    print("Authentication error")
            else:
                print("Failed to read the card")
        else:
            print("Waiting for card...")

if __name__ == "__main__":
    main()
