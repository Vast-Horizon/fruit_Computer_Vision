"""
This script is intended to be used on raspberry pi only.
This script is a standalone side-project about using HX711 and load cell to accurately measure object weight.
The reason it's included in this project is that the final goal is to
                combine ML and weight sensor to calculate the price of fruits the camera sees.
"""
from gpiozero import DigitalInputDevice, DigitalOutputDevice
import time

# Define GPIO pins using gpiozero
dt = DigitalInputDevice(14)
sck = DigitalOutputDevice(15)
calibration_factor = 1

def read_HX711():
    count = 0
    
    # Ensure SCK is Low
    sck.off()
    
    while dt.is_active:
        # Wait for DT to go low
        pass
    
    for i in range(24):
        # Pulse the SCK pin
        sck.on()
        count = count << 1
        sck.off()
        if dt.is_active:
            count += 1
    
    # 25th pulse at SCK to set the gain back to channel A, gain 128
    sck.on()
    count = count^0x800000  # flips the 24th bit
    sck.off()
    value = abs(count)
    
    
    return value

def zero_scale():
    tare = read_HX711()
    return tare

def calibrate_scale(known_weight, readings=10):
    # Calibrate the scale using a known weight using 10 readings
    measured_values = [read_HX711() for _ in range(readings)]
    average_value = sum(measured_values) / readings
    calibration_factor = known_weight / average_value
    return calibration_factor
    
    
try:
    '''
    To calibrate the scale, flow the steps:
    1. uncomment the code below
    2. place 1kg on the scale
    3. run the code
    4. record the calibration factor
    5. take out the weight nd record the Corrected reading
    5. stope the code and upate the calibration_factor valuable
    6. update the offset_factor valuable
    7. recomment out the code
    For example, 0.00011765484757443882 for calibration_factor, get a reading of 49.5 as the offset_factor
    
    '''
    
    '''
    print("Zeroing scale, please ensure it's unloaded.")
    tare = zero_scale()
    print("Place a known weight on the scale for calibration.")
    time.sleep(5)  # Give time to place the weight
    calibration_factor = calibrate_scale(known_weight=1000)  # Enter the known weight in grams
    print(f"Calibration Factor: {calibration_factor}") 
    '''
    
    tare = zero_scale()
    calibration_factor = 0.00011765484757443882
    offset_factor = 49.5
    tare_Flag = True

    while True:
        value = read_HX711()
        if tare_Flag:
            corrected_value = abs(value - tare) * calibration_factor/offset_factor * 1000
            print("Raw:", value, " Corrected:", corrected_value, "g")
        if not tare_Flag:
            corrected_value = abs(value - 19948.6) * calibration_factor / offset_factor * 1000
            print("Raw:", value, " Corrected:", corrected_value, "g")
        time.sleep(0.5)


except KeyboardInterrupt:
    print("\nProgram exited cleanly")
