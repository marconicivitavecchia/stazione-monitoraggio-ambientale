import time
import network
import ntptime

def random_string(length=8):
    import uos
    _randomstring = ''
    _source = 'abcdefghijklmnopqrstuvwxyz'
    x = 0
    while x < length:
        _randomstring = _randomstring + _source[uos.urandom(1)[0] % len(_source)]
        x += 1
    return _randomstring

def unique_id(wlan_mac):
    import ubinascii
    return ubinascii.hexlify(wlan_mac).decode()


def wifi_connect(ssid, key):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid, key)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.1)
    ip = sta_if.ifconfig()[0]
    wlan_mac = sta_if.config('mac')
    ntptime.settime()
    return (ip,wlan_mac)


# Date and time
# Time is a tuple like this:
# (year, month, mday, hour, minute, second, weekday, yearday)
# gmtime() is a UTC tuple, localtime() is a local time tuple
# Tuple format is
# (year, month 1-12, day of the month 1-31, hour 0-23, minutes 0-59,
# seconds 0-59, day of the week 0-6 (mon-sun), day of the year 1-366)
def date_time():
    date_time = time.localtime()
    # anno, mese, giorno, ora, minuti, secondi, week_day, year_day = time.localtime()
    return date_time

