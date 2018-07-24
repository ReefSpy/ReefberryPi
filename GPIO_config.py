import RPi.GPIO as GPIO

# GPIO pins
dht11 = 14        # for dht11 temp and humidity sensor
SPICLK = 18       # for MCP3008 ADC
SPIMISO = 23      # for MCP3008 ADC
SPIMOSI = 24      # for MCP3008 ADC
SPICS = 25        # for MCP3008 ADC
relay_1 = 19     

# MCP3008 pins
ph_adc = 0

def initGPIO():
    # turn off warnings
    GPIO.setwarnings(False)
    
    # set pin mode
    GPIO.setmode(GPIO.BCM)

    # set up the SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)

    # set up pins for relay controls
    GPIO.setup(relay_1, GPIO.OUT)
