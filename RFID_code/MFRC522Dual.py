#!/usr/bin/env python
# -*- coding: utf8 -*-
import RPi.GPIO as GPIO
import spidev

class MFRC522:

    MI_OK = 0
    MI_NOTAGERR = 1
    MI_ERR = 2

    # Initialize the RFID reader
    def __init__(self, spi_bus=0, spi_device=0, rst_pin=22, cs_pin=24):
        self.rst_pin = rst_pin
        self.cs_pin = cs_pin

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.cs_pin, GPIO.OUT)

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000

        # Reset the RFID reader
        self.MFRC522_Reset()

    def MFRC522_Reset(self):
        self.Write_MFRC522(0x01, 0x0F)

    def Write_MFRC522(self, addr, val):
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.xfer([((addr << 1) & 0x7E), val])
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def Read_MFRC522(self, addr):
        GPIO.output(self.cs_pin, GPIO.LOW)
        val = self.spi.xfer([((addr << 1) & 0x7E) | 0x80, 0])
        GPIO.output(self.cs_pin, GPIO.HIGH)
        return val[1]

    def MFRC522_Request(self, req_mode):
        self.Write_MFRC522(0x0D, 0x07)
        (status, back_data) = self.MFRC522_ToCard(0x0C, [req_mode])
        return (status, back_data)

    def MFRC522_ToCard(self, command, send_data):
        # Implementation of the communication logic
        pass

    def MFRC522_Anticoll(self):
        back_data = []
        ser_num_check = 0
        ser_num = []

        self.Write_MFRC522(0x0D, 0x00)

        back_len = 0
        (status, back_data) = self.MFRC522_ToCard(0x0C, [0x93, 0x20])

        if status == self.MI_OK:
            if len(back_data) == 5:
                for i in range(4):
                    ser_num_check = ser_num_check ^ back_data[i]
                if ser_num_check != back_data[4]:
                    status = self.MI_ERR
            else:
                status = self.MI_ERR

        return (status, back_data)

    def MFRC522_SelectTag(self, uid):
        buf = [0x93, 0x70] + uid[:5]
        buf.append(0x00)
        self.Write_MFRC522(0x0D, 0x00)
        self.MFRC522_ToCard(0x0C, buf)

    def MFRC522_StopCrypto1(self):
        self.Write_MFRC522(0x0C, 0x00)

    def MFRC522_Auth(self, auth_mode, block_addr, sector_key, ser_num):
        buff = [auth_mode, block_addr] + sector_key[:6] + ser_num[:4]
        (status, back_data) = self.MFRC522_ToCard(0x0E, buff)
        return status

    def MFRC522_Read(self, block_addr):
        recv_data = [0x30, block_addr]
        (status, back_data) = self.MFRC522_ToCard(0x0C, recv_data)
        if not (status == self.MI_OK):
            print("Error while reading!")
        return back_data

    def MFRC522_Write(self, block_addr, write_data):
        buff = [0xA0, block_addr] + write_data[:16]
        (status, back_data) = self.MFRC522_ToCard(0x0C, buff)
        if not (status == self.MI_OK):
            print("Error while writing!")
