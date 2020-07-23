#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import time
import subprocess
import Adafruit_DHT
from RPLCD.i2c import CharLCD

sensor_args = {"11": Adafruit_DHT.DHT11,
               "22": Adafruit_DHT.DHT22,
               "2302": Adafruit_DHT.AM2302}

sensor_type = sensor_args["11"]
sensor_channel = 24

lcd_height = 4
lcd_width = 20

# custom characters
degrees = (
    0b11100,
    0b10100,
    0b11100,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)


class Sensor(object):
    def __init__(self, type, channel):
        super(Sensor, self).__init__()
        self.type = type
        self.channel = channel

    def get(self):
        try:
            humidity, temperature = Adafruit_DHT.read_retry(self.type, self.channel)
            return humidity, temperature

        except Exception as e:
            error_message = "Fallo al intentar leer datos"
            print(error_message)
            return error_message
            sys.exit(1)

def center_message(message):
    spaces = int((lcd_width - len(message)) / 2)
    return "{}{}".format(" " * spaces, message)

def sensor_data(sensor, lcd):
    response = ["", "", "", ""]
    response[0] = center_message("Datos del tiempo")

    try:
        humidity, temperature = sensor.get()
        humidity = "%.0f" % humidity
        temperature = "%.0f" % temperature
        response[2] = "Humedad: {}%".format(humidity)
        response[3] = "Temperatura: {}{}".format(temperature, "\x00")

    except Exception as e:
        response[2] = "Problemas al leer sensor"

    finally:
        return response

def clock():
    response = ["", "", "", ""]
    response[0] = center_message("Fecha y hora")
    response[2] = "Fecha: {}".format(time.strftime("%d %b %Y", time.localtime()))
    response[3] = "Hora: {}".format(time.strftime("%H:%M:%S", time.localtime()))

    return response

def ip():
    response = ["", "", "", ""]
    response[0] = "IP"
    FNULL = open(os.devnull, "w")
    response[2] = response[2] = subprocess.check_output(["curl", "-s", "ifconfig.me"]).split()[0].decode("utf-8")

    return response

def show(lcd, message):
    for r in range(4):
        lcd.cursor_pos = tuple([r, 0])
        lcd.write_string(message[r])


def main():
    sensor = Sensor(sensor_type, sensor_channel)
    lcd = CharLCD("PCF8574", 0x27)

    # add custom chars
    lcd.create_char(0, degrees)

    menu = {
        1: sensor_data(sensor, lcd),
        2: clock(),
        3: ip()
    }

    for i in menu.keys():
        show(lcd, menu[i])
        time.sleep(3)
        lcd.clear()


if __name__ == "__main__":
    main()
