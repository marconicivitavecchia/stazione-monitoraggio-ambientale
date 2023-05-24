"""
IIS Marconi Civitavecchia
A.S. 2022/2023
Teacher course Python-IoT-AI

ScuolaFutura codes:
- ID.120087 Modulo 1: Python
- ID.120182 Modulo 2: IoT
- ID.120238 Modulo 3: AI

Link GitHub: https://github.com/marconicivitavecchia/stazione-monitoraggio-ambientale

Credits
MicroPython IoT Weather Station Example for Wokwi.com
https://wokwi.com/arduino/projects/322577683855704658

OTA updater for ESP32 running Micropython by David Flory
Tutorial: https://randomnerdtutorials.com/esp32-esp8266-micropython-ota-updates/
"""

from machine import UART
from machine import reset as machine_reset

# Manage debug
import esp

esp.osdebug(None)  # turn off vendor O/S debugging messages
# esp.osdebug(0)          # redirect vendor O/S debugging messages to UART(0)

# Run Garbage Collector
import gc

gc.collect()

from config import WIFI_SSID, WIFI_PASSWORD  # secret configuration variables
from utils import bin2hex, wifi_connect, random_string, date_time, get_sensor_id
import ujson
import time

# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-" + random_string()
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = "pm-sds011"


# Serial configuration
print("Configuring serial...")
uart = UART(1, baudrate=9600, rx=16, tx=17)

# Sensor configuration
print("Configuring sensor...")
import sds011

dust_sensor = sds011.SDS011(uart)
dust_sensor.wake()
# Following for-cycle is needed because reading from sensors could be
# temporarly not available
for numero in range(20):
    dust_sensor.read()
pmSensorID = get_sensor_id(dust_sensor)


# WiFi configuration
print(f"Connecting to WiFi {WIFI_SSID}...", end="")
(ip, wlan_mac) = wifi_connect(WIFI_SSID, WIFI_PASSWORD)
print(" Connected!")
print(f"ip: {ip}, mac: {bin2hex(wlan_mac)}")
esp32_unique_id = bin2hex(wlan_mac)

# MQTT init
from umqtt.simple import MQTTClient

print(f"Connecting to MQTT server with client id {MQTT_CLIENT_ID}...", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()
print("Connected!")

while True:
    # Returns NOK if no measurement found in reasonable time
    status = dust_sensor.read()
    # Returns NOK if checksum failed
    pkt_status = dust_sensor.packet_status

    if status == False:
        print("Measurement failed.")
        time.sleep(5)
        continue
    elif pkt_status == False:
        print("Received corrupted data.")
        time.sleep(5)
        continue

    # mqtt message packing
    anno, mese, giorno, ora, minuti, secondi, week_day, year_day = date_time()
    message = ujson.dumps(
        {
            "boardID": esp32_unique_id,
            "timestamp": f"{anno}-{mese:02d}-{giorno:02d}T{ora:02d}:{minuti:02d}:{secondi:02d}",
            "pmSensor": {
                "sensorID": pmSensorID,
                "PM10": dust_sensor.pm10,
                "PM25": dust_sensor.pm25,
            },
        }
    )
    print(f"Reporting to MQTT topic {MQTT_TOPIC}: {message}")

    # mqtt message publishing
    try:
        client.publish(MQTT_TOPIC, message)
    except OSError as e:
        print(e)
        print("Restarting board in 10 seconds...")
        time.sleep(10)
        machine_reset()

    time.sleep(5)
