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

# Manage debug
import esp
esp.osdebug(None)  # turn off vendor O/S debugging messages
# esp.osdebug(0)          # redirect vendor O/S debugging messages to UART(0)

# Run Garbage Collector
import gc
gc.collect()

from config import WIFI_SSID, WIFI_PASSWORD  # secret configuration variables
from utils import unique_id, wifi_connect, random_string, date_time
import ujson
import time

# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-"+random_string()
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = "pm-sds011"


# Serial configuration
print("Configuring serial...")
from machine import UART
uart = UART(1, baudrate = 9600, rx = 16, tx = 17)

# Sensor configuration
print("Configuring sensor...")
import sds011
dust_sensor = sds011.SDS011(uart)
dust_sensor.wake()
# Following for-cycle is needed because reading from sensors could be
# temporarly not available
for numero in range(20):
    dust_sensor.read()

# WiFi configuration
print("Connecting to WiFi...", end="")
(ip,wlan_mac) = wifi_connect(WIFI_SSID,WIFI_PASSWORD)
print(" Connected!")
print(f"ip: {ip}, mac: {wlan_mac}")
esp32_unique_id = unique_id(wlan_mac)

# MQTT init
from umqtt.simple import MQTTClient
print("Connecting to MQTT server...")
print(f"ClientID: {MQTT_CLIENT_ID}")
print(f"Boroker: {MQTT_BROKER}")
print(f"Topic: {MQTT_TOPIC}")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()
print("Connected!")

while True:
    #Returns NOK if no measurement found in reasonable time
    status = dust_sensor.read()
    #Returns NOK if checksum failed
    pkt_status = dust_sensor.packet_status

    if(status == False):
        print('Measurement failed.')
    elif(pkt_status == False):
        print('Received corrupted data.')

    # mqtt message packing
    anno, mese, giorno, ora, minuti, secondi, week_day, year_day = date_time()
    message = ujson.dumps(
        {
            "ID": esp32_unique_id,
            "timestamp": f"{anno}-{mese:02d}-{giorno:02d}T{ora:02d}:{minuti:02d}:{secondi:02d}",
            "PM10": dust_sensor.pm10,
            "PM25": dust_sensor.pm25,
        }
    )
    print(f"Reporting to MQTT topic {MQTT_TOPIC}: {message}")

    # mqtt message publishing
    client.publish(MQTT_TOPIC, message)
    
    time.sleep(5)