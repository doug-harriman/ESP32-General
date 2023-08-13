import machine
import onewire
import ds18x20
import time

# Connect to sensor
class SensorTemperature:

    def __init__(self,pin:int=25):

        self._pin = machine.Pin(pin)

    def connect(self):

        # Connect to sensor
        ow = onewire.OneWire(self._pin)
        self._sensor = ds18x20.DS18X20(ow)

        # Read sensor address
        # If there is more than one sensor, multiple addresses will be returned.
        self._addr = self._sensor.scan()

        if len(self._addr) != 1:
            raise Exception("Sensor not found")

        self._addr = self._addr[0]

    def read(self):
        """
        Read temperature from sensor.

        Returns:
            float: Temperature in degrees Fahrenheit.
        """

        self._sensor.convert_temp()
        time.sleep_ms(750)
        temp_C = self._sensor.read_temp(self._addr)

        temp_F = (temp_C * 1.8) + 32

        return temp_F
