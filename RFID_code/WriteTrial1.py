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

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
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

        # Print UID
        print("Card read UID: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3]))

        # Check if the UID matches the specific one (66, 190, 199, 247)
        if uid[0] == 66 and uid[1] == 190 and uid[2] == 199 and uid[3] == 247:
            print("This is the correct card.")

            # This is the default key for authentication
            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate for sector 8
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            if status == MIFAREReader.MI_OK:

                # Prepare data to write "Apple" and "2.99"
                # Convert the string "Apple" and "2.99" to bytes and pad to 16 bytes each
                apple_data = [ord(c) for c in "Apple"] + [0x00] * (16 - len("Apple"))
                price_data = [ord(c) for c in "2.99"] + [0x00] * (16 - len("2.99"))

                # Write "Apple" to block 8
                print("Writing 'Apple' to block 8...")
                MIFAREReader.MFRC522_Write(8, apple_data)

                # Verify by reading block 8
                print("Verifying 'Apple' in block 8:")
                MIFAREReader.MFRC522_Read(8)

                # Write "2.99" to block 9
                print("Writing '2.99' to block 9...")
                MIFAREReader.MFRC522_Write(9, price_data)

                # Verify by reading block 9
                print("Verifying '2.99' in block 9:")
                MIFAREReader.MFRC522_Read(9)

                # Stop Crypto1 when done
                MIFAREReader.MFRC522_StopCrypto1()

                # End reading after writing to the card
                continue_reading = False

            else:
                print("Authentication error")

        else:
            print("This is not the correct card.")
