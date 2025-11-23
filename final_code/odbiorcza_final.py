# stacja odbiorcza
import time
import RPi.GPIO as GPIO
import serial

import board
import busio
import digitalio
from adafruit_ssd1306 import SSD1306_SPI
from PIL import Image, ImageDraw, ImageFont


LED_PIN = 17        
BUZZER_PIN = 18     

TEMP_LIMIT = 28.0   # C - próg alarmu
HUM_LIMIT = 70.0    # %  - próg alarmu

OLED_WIDTH = 128
OLED_HEIGHT = 64

OLED_DC_PIN = board.D25
OLED_RESET_PIN = board.D24
OLED_CS_PIN = board.CE0

# port szeregowy z HC-12
SERIAL_PORT = "/dev/serial0"
SERIAL_BAUD = 9600


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)


ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)


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
    """Krótkie mignięcie diody przy każdym poprawnym odebraniu danych."""
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(LED_PIN, GPIO.LOW)

def set_buzzer(on: bool):
    GPIO.output(BUZZER_PIN, GPIO.HIGH if on else GPIO.LOW)

def update_oled(temperature, humidity, alarm, ok_read=True):
    """Aktualizacja wyświetlacza OLED."""
    draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)

    if ok_read:
        line1 = f"Temp: {temperature:.1f} C"
        line2 = f"Wilg: {humidity:.1f} %"
    else:
        line1 = "Brak danych"
        line2 = "HC-12"

    line3 = "ALARM!" if alarm else "OK"

    draw.text((0, 0), line1, font=font, fill=255)
    draw.text((0, 16), line2, font=font, fill=255)
    draw.text((0, 32), line3, font=font, fill=255)

    oled.image(image)
    oled.show()

def parse_line(line: str):
    """
    Oczekiwany format z Pico:
    T:23.0;H:44.0
    Zwraca (ok, temp, hum)
    """
    try:
        line = line.strip()
        if not line:
            return False, None, None

        parts = line.split(";")
        if len(parts) != 2:
            return False, None, None

        t_part = parts[0]  # "T:23.0"
        h_part = parts[1]  # "H:44.0"

        if not (t_part.startswith("T:") and h_part.startswith("H:")):
            return False, None, None

        temp = float(t_part[2:])
        hum = float(h_part[2:])
        return True, temp, hum
    except Exception:
        return False, None, None

def read_remote_with_retries(retries=5):
    """
    Próbuje kilka razy odczytać linijkę z HC-12
    i sparsować ją do (temp, hum).
    """
    for _ in range(retries):
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue

        ok, temp, hum = parse_line(line)
        if ok:
            return True, temp, hum

    return False, None, None


try:
    print("Oczekuję na dane z HC-12...")

    while True:
        ok, temperature, humidity = read_remote_with_retries()

        if ok:
            blink_led()

            print(f"Odebrano -> Temp: {temperature:.1f} °C  Wilg: {humidity:.1f} %")

            alarm = (temperature > TEMP_LIMIT) or (humidity > HUM_LIMIT)
            set_buzzer(alarm)
            update_oled(temperature, humidity, alarm, ok_read=True)

            print("ALARM:", "TAK" if alarm else "NIE")
        else:
            print("Brak poprawnych danych z HC-12")
            alarm = False
            set_buzzer(False)
            update_oled(0, 0, alarm, ok_read=False)

        print("---------------------------")
        time.sleep(1)

except KeyboardInterrupt:
    print("Zamykanie...")

finally:
    set_buzzer(False)
    GPIO.cleanup()
    oled.fill(0)
    oled.show()
    ser.close()

