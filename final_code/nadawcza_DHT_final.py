#stacja badawcza z antena i DHT
import machine
import utime
import dht



PIN_DHT = 16        
PIN_LED = 14        

UART_PORT = 0
UART_TX = 0         
UART_RX = 1         
UART_BAUD = 9600    

MEASURE_INTERVAL = 5  


sensor = dht.DHT11(machine.Pin(PIN_DHT))
led = machine.Pin(PIN_LED, machine.Pin.OUT)

uart = machine.UART(
    UART_PORT,
    baudrate=UART_BAUD,
    tx=machine.Pin(UART_TX),
    rx=machine.Pin(UART_RX)
)


def blink():
    """Krótkie mignięcie diody przy pomiarze."""
    led.value(1)
    utime.sleep(0.1)
    led.value(0)

def send_measurement(temp, hum):
    """
    Wysyła dane przez HC-12 w prostym formacie tekstowym.
    Np: T:23.0;H:45.0
    """
    msg = "T:{:.1f};H:{:.1f}\n".format(temp, hum)
    uart.write(msg)
    # dla debugowania przez USB:
    print("Wyslano:", msg.strip())


try:
    sensor.measure()
    _ = sensor.temperature()
    _ = sensor.humidity()
    utime.sleep(1)
except OSError:
    pass

while True:
    try:
        blink()

        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        print("Temp:", temp, "C  Wilg:", hum, "%")
        send_measurement(temp, hum)

    except OSError as e:
      
        print("Blad odczytu DHT11:", e)

    utime.sleep(MEASURE_INTERVAL)

