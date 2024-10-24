import time
import random
try:
    from gpiozero import DigitalInputDevice, DigitalOutputDevice
except ModuleNotFoundError:
    print('Weighting Class Not in raspberry Pi environment')

class Weighting:
    def __init__(self, calibration_factor, dt_pin=14, sck_pin=15):
        self.calibration_factor = calibration_factor
        self.offset_factor = 49.5
        self.running = True  # Flag to control the loop
        self.current_weight = 0  # Store the latest weight
        self.simulation_mode = False
        try:
            self.dt = DigitalInputDevice(dt_pin)
            self.sck = DigitalOutputDevice(sck_pin)
        except NameError:
            pass

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
            if not self.simulation_mode:
                tare = self.zero_scale()

            while self.running:
                if self.simulation_mode:
                    self.simulate_weight_output()
                else:
                    value = self.read_HX711()
                    self.current_weight = abs(value - tare) * self.calibration_factor / self.offset_factor * 1000
                    #print(f"{self.current_weight}g")
                    time.sleep(0.2)
        except KeyboardInterrupt:
            pass
        finally:
            print("Weighting stopped.")

    def get_weight(self):
        return self.current_weight

    def stop(self):
        self.running = False

    def simulate_weight_output(self):
        """Simulates random weight readings for testing purposes."""
        self.current_weight = random.uniform(1, 10)

    def testing_only(self, enable_simulation=True):
        self.simulation_mode = enable_simulation