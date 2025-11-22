import machine
import utime
import dht

sensor = dht.DHT11(machine.Pin(16))
led = machine.Pin(14, machine.Pin.OUT)

while True:
    try:
        led.value(1)
        utime.sleep(0.1)
        led.value(0)
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        print("Temperatura:", temp, "°C")
        print("Wilgotność:", hum, "%")
        print("--------------------------")

    except OSError as e:
        print("Błąd odczytu z czujnika:", e)

    utime.sleep(2)  
