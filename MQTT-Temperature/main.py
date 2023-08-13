# main.py 
print('main.py')

import machine
import network
import time
import ubinascii
from umqtt.simple import MQTTClient
from sensor_temperature import SensorTemperature
from secret import WIFI_SSID, WIFI_PASS


# Configuration
# NOTE: There's a bug in nework.hostname where it will not accept a variable
DEVICE = "home-office-tmp"
MQTT_HOST = "192.168.0.120"
MQTT_PORT = 1885
SLEEP = 60*5  # [sec], time between temperature readings

# Create network object.
print('Configuring network interface')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
time.sleep(1)
if len(DEVICE) > 15:
    raise ValueError("Device name must be 15 characters or less.")
wlan.config(hostname=DEVICE)

# Look for WiFi network.
nets = wlan.scan()
nets = [n[0].decode() for n in nets]
if WIFI_SSID not in nets:
    print(f"WiFi network not found: {WIFI_SSID}")
    machine.reset()
else:
    print(f"Found WiFi network: {WIFI_SSID}, trying to connect...")

# Wait for connection
retries = 5
wlan.connect(WIFI_SSID, WIFI_PASS)
time.sleep(3)
while not wlan.isconnected() and retries > 0:
    print(f'Unable to connect to WiFi {WIFI_SSID}, retry ({retries})')
    retries -= 1
    time.sleep(5)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    

if not wlan.isconnected():
    print(f"Failed to connect to WiFi network: {WIFI_SSID}")
    machine.reset()

print(f'WiFi connected as:{wlan.ifconfig()}')

# MQTT Connection
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
mqtt = MQTTClient(MQTT_CLIENT_ID, 
                  MQTT_HOST, 
                  port=MQTT_PORT,
                  keepalive=60)
mqtt.connect()

# MQTT Topic
topic = bytes(f"device/{network.hostname()}", "utf-8")
print(f"MQTT topic: {topic}")

# Connect to temperature sensor.
sensor=SensorTemperature()
sensor.connect()

# Publish loop.
while True:
    # Read temperature.
    temp = sensor.read()
    print(f"{DEVICE} Temperature: {temp:0.1f}")

    # Note: We're not keeping time on the ESP32, so we're not going to
    #       publish a timestamp.  The server will add the timestamp
    #       when it receives the message.

    # Render JSON message.
    msg = "{"  # noqa: E501
    msg += f'"temperature": {int(temp+0.5)},'  # noqa: E501
    msg += f'"battery_soc": 100'  # noqa: E501
    msg += "}"  # noqa: E501

    # Publish temperature.
    mqtt.publish(topic,msg)

    # Sleep.
    print(f'Sleeping for {SLEEP} sec')
    time.sleep(SLEEP)


