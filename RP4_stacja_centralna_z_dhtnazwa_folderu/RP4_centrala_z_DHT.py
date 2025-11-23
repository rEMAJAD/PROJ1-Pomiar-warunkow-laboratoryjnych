import time
import RPi.GPIO as GPIO
import dht11

import board
import busio
import digitalio
from adafruit_ssd1306 import SSD1306_SPI
from PIL import Image, ImageDraw, ImageFont

DHT_PIN = 4 

LED_PIN = 17       
BUZZER_PIN = 18    

# Progi alarmu
TEMP_LIMIT = 28.0  # C
HUM_LIMIT = 70.0   # %

OLED_WIDTH = 128
OLED_HEIGHT = 64

OLED_DC_PIN = board.D25
OLED_RESET_PIN = board.D24
OLED_CS_PIN = board.CE0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)

sensor = dht11.DHT11(pin=DHT_PIN)

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)

dc_pin = digitalio.DigitalInOut(OLED_DC_PIN)
reset_pin = digitalio.DigitalInOut(OLED_RESET_PIN)
cs_pin = digitalio.DigitalInOut(OLED_CS_PIN)

oled = SSD1306_SPI(OLED_WIDTH, OLED_HEIGHT, spi, dc_pin, reset_pin, cs_pin)

oled.fill(0)
oled.show()

image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def blink_led():
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(LED_PIN, GPIO.LOW)

def set_buzzer(on: bool):
    GPIO.output(BUZZER_PIN, GPIO.HIGH if on else GPIO.LOW)

def update_oled(temperature, humidity, alarm, ok_read=True):
    draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)

    if ok_read:
        line1 = f"Temp: {temperature:.1f} C"
        line2 = f"Wilg: {humidity:.1f} %"
    else:
        line1 = "Blad odczytu"
        line2 = "DHT11"

    line3 = "ALARM!" if alarm else "OK"

    draw.text((0, 0), line1, font=font, fill=255)
    draw.text((0, 16), line2, font=font, fill=255)
    draw.text((0, 32), line3, font=font, fill=255)

    oled.image(image)
    oled.show()

def read_dht_with_retries(retries=5, delay=0.5): # -----> zabezpieczenie przed
    for _ in range(retries):
        result = sensor.read()
        if result.is_valid():
            return True, float(result.temperature), float(result.humidity)
        time.sleep(delay)
    return False, None, None

try:
    print("Pomijam pierwszy pomiar...")
    read_dht_with_retries()   
    time.sleep(1)

    while True:
        blink_led()

        ok, temperature, humidity = read_dht_with_retries()

        if ok:
            print(f"Temp: {temperature:.1f} °C")
            print(f"Wilg: {humidity:.1f} %")

            alarm = (temperature > TEMP_LIMIT) or (humidity > HUM_LIMIT)
            set_buzzer(alarm)

            update_oled(temperature, humidity, alarm, ok_read=True)

            print("ALARM:", "TAK" if alarm else "NIE")
        else:
            print("Błąd odczytu DHT11 po kilku próbach")
            alarm = False
            set_buzzer(False)
            update_oled(0, 0, alarm, ok_read=False)

        print("---------------------------")
        time.sleep(5)  # -------> Czas miedzy pomiarami 

except KeyboardInterrupt:
    print("Zamykanie")

finally:
    set_buzzer(False)
    GPIO.cleanup()
    oled.fill(0)
    oled.show()

