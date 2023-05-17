from machine import UART
import sds011
import network
import time
from umqtt.simple import MQTTClient
import struct
import ntptime
############ INIZIALIZZAZIONE DELLA SERIALE #############################
uart = UART(1, baudrate=9600, rx=16, tx=17)
#########################################################################

############ START DEFINIZIONE FUNZIONI #################################
# wifi init
def wifi_connect(ssid, key):
    sta_if = network.WLAN(network.STA_IF)
    print("Connecting to WiFi")
    sta_if.active(True)
    sta_if.connect(ssid, key)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.1)
    print(" Connected!")

# DATA E ORA:
# Per il tempo viene restituita la tupla:
# (year, month, mday, hour, minute, second, weekday, yearday)
# gmtime() restituisce una tupla in UTC, localtime() restituisce una tupla local time.
# Il formato della tupla è:
# (anno, mese da 1-12, giorno del mese da 1-31, ora tra 0-23, minuti tra 0-59,
# secondi tra 0-59, giorno settimana tra 0-6 per lun-dom, giorno dell'anno tra1-366)
def date_hour():
  ntptime.settime()
  date_time = time.localtime()
  #anno, mese, giorno, ora, minuti, secondi, week_day, year_day = time.localtime()
  return date_time
############ END DEFINIZIONE FUNZIONI ###################################

############ START CONNECTRING ##########################################
wifi_connect("<ssid>", "<key>")
#########################################################################

############ CONNESSIONE A MQTT #########################################
# MQTT Server Parameters
MQTT_CLIENT_ID = "clientId-d30TD4Chy2"
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = "pm-sds011-test1"

# mqtt init
print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()
print("Connected!")
#########################################################################

############ SENSORE COLLEGATO ALLA SERIALE #############################
dust_sensor = sds011.SDS011(uart)
# dust_sensor.sleep()
dust_sensor.wake()
# Il ciclo for è necessario perche' le letture dust_sensor.id1 e
# dust_sensor.id2 che seguono potrebbero essere momentaneamente
# non disponibili con conseguente errore
for numero in range(20):
  dust_sensor.read()
#########################################################################

############ LETTURA ID SENSORE (vedi modulo sds011 modificato) #########
id1 = hex(dust_sensor.id1)
id2 = hex(dust_sensor.id2)
id_sensor = id1[2:].upper() + id2[2:].upper()
# print_idSensor()
#########################################################################

############ CICLO DI LETTURA ###########################################
while True:
    # Datasheet says to wait for at least 30 seconds...
    #print("Start fan for 5 seconds.")
    dust_sensor.wake()
    # time.sleep(5)

    # Returns NOK if no measurement found in reasonable time
    status = dust_sensor.read()
    # Returns NOK if checksum failed
    pkt_status = dust_sensor.packet_status

    # Stop fan
    # dust_sensor.sleep()

    if status == False:
        print("Measurement failed.")
    elif pkt_status == False:
        print("Received corrupted data.")
    # mqtt message packing
    #message = ujson.dumps(
    #  {
    #    "ID SENSORE": id_sensor,
    #    "PM10": dust_sensor.pm10,
    #    "PM25": dust_sensor.pm25,
    #  }
    #)
    #print("{}:".format(message))

    date_hour()
    anno, mese, giorno, ora, minuti, secondi, week_day, year_day = date_hour()
    #message = f'{giorno}{"/"}{mese}{"/"}{anno}{" "}{ora}{":"}{minuti}{" -- ID sensore: "}{id_sensor}{" -- PM2.5: "}{dust_sensor.pm10}{" -- PM10: "}{dust_sensor.pm10}'
    message = "{}/{}/{} [{}:{}] -- ID: {} -- PM2.5: {} -- PM10: {}"\
      .format(giorno,mese,anno,ora+2,minuti,id_sensor,dust_sensor.pm25,dust_sensor.pm10)
    print(message)
    client.publish(MQTT_TOPIC, message)
    time.sleep(2)
