import time
from gpiozero import DigitalInputDevice, DigitalOutputDevice

class Weighting:
    def __init__(self, calibration_factor, dt_pin=14, sck_pin=15):
        self.dt = DigitalInputDevice(dt_pin)
        self.sck = DigitalOutputDevice(sck_pin)
        self.calibration_factor = calibration_factor
        self.offset_factor = 49.5
        self.running = True  # Flag to control the loop

    def read_HX711(self):
        count = 0
        self.sck.off()
        while self.dt.is_active:
            pass
        for i in range(24):
            self.sck.on()
            count = count << 1
            self.sck.off()
            if self.dt.is_active:
                count += 1
        self.sck.on()
        count = count ^ 0x800000  # flips the 24th bit
        self.sck.off()
        return abs(count)

    def zero_scale(self):
        return self.read_HX711()

    def calibrate_scale(self, known_weight, readings=10):
        measured_values = [self.read_HX711() for _ in range(readings)]
        average_value = sum(measured_values) / readings
        return known_weight / average_value

    def start(self):
        try:
            tare = self.zero_scale()
            while self.running:
                value = self.read_HX711()
                corrected_value = abs(value - tare) * self.calibration_factor / self.offset_factor * 1000
                print(f"{corrected_value}g")
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            print("Weighting stopped.")

    def stop(self):
        self.running = False
