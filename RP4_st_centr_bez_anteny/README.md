# Stacja pomiaru temperatury i wilgotności (Raspberry Pi 4 + DHT11 + OLED + buzzer)

## Wykorzystane elementy

- Raspberry Pi 4
- DHT11 (czujnik temperatury i wilgotności)
- Dioda LED + rezystor 220–330 Ω
- Buzzer aktywny (on/off)
- Wyświetlacz OLED SSD1306, wersja **SPI** (piny: VCC, GND, DIN, CLK, CS, D/C, RES)
- Kilka przewodów połączeniowych

---

## Połączenia (GPIO – numeracja BCM)

### DHT11

- **VCC** → 3.3 V  
- **GND** → GND  
- **DATA** → **GPIO 4**

---

### LED

- anoda LED → rezystor → **GPIO 17**  
- katoda LED → GND  

---

### Buzzer (aktywny)

- **+** → **GPIO 18**  
- **–** → GND  

---

### OLED SSD1306 (SPI)

- **VCC** → 3.3 V  
- **GND** → GND  
- **DIN** → **GPIO 10** (MOSI, pin 19)  
- **CLK** → **GPIO 11** (SCLK, pin 23)  
- **CS** → **GPIO 8** (CE0, pin 24)  
- **D/C** → **GPIO 25** (pin 22)  
- **RES** → **GPIO 24** (pin 18)  
- **NC** → niepodłączone  

---

## Wymagane biblioteki (Raspberry Pi OS)

Instalacja z terminala na Raspberry Pi:

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev python3-smbus i2c-tools python3-pil

pip3 install --break-system-packages dht11 RPi.GPIO adafruit-blinka adafruit-circuitpython-ssd1306 pillow

