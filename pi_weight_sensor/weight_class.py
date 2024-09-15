from gpiozero import DigitalInputDevice, DigitalOutputDevice
import time

class Weighting:
    def __init__(self, dt_pin=14, sck_pin=15, calibration_factor=1.0):
        # Initialize GPIO pins
        self.dt = DigitalInputDevice(dt_pin)
        self.sck = DigitalOutputDevice(sck_pin)
        self.calibration_factor = calibration_factor
        self.tare = 0
        self.offset_factor = 49.5  # The factor for correcting raw values

    def read_HX711(self):
        count = 0
        self.sck.off()

        while self.dt.is_active:
            # Wait for DT to go low
            pass

        for _ in range(24):
            # Pulse the SCK pin
            self.sck.on()
            count = count << 1
            self.sck.off()
            if self.dt.is_active:
                count += 1

        # 25th pulse at SCK to set the gain back to channel A, gain 128
        self.sck.on()
        count = count ^ 0x800000  # flips the 24th bit
        self.sck.off()

        return abs(count)

    def zero_scale(self):
        # Tare function to zero the scale
        self.tare = self.read_HX711()

    def calibrate_scale(self, known_weight, readings=10):
        # Calibrate the scale using a known weight and a number of readings
        measured_values = [self.read_HX711() for _ in range(readings)]
        average_value = sum(measured_values) / readings
        self.calibration_factor = known_weight / average_value

    def get_weight(self):
        # Get the corrected weight value in grams
        raw_value = self.read_HX711()
        corrected_value = abs(raw_value - self.tare) * self.calibration_factor / self.offset_factor * 1000
        return raw_value, corrected_value

    def start(self, interval=0.5):
        # Start measuring the weight at a regular interval
        try:
            self.zero_scale()
            print("Scale zeroed. Starting weight measurements...")

            while True:
                raw, corrected = self.get_weight()
                print(f"Raw: {raw}, Corrected: {corrected:.2f} g")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nProgram exited cleanly")



if __name__ == "__main__":
    weighting = Weighting(calibration_factor=0.00011765484757443882)
    weighting.start()
