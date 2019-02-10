import RPi.GPIO as GPIO

# GPIO pins
dht11 = 14        # for dht11 temp and humidity sensor
SPICLK = 18       # for MCP3008 ADC
SPIMISO = 23      # for MCP3008 ADC
SPIMOSI = 24      # for MCP3008 ADC
SPICS = 25        # for MCP3008 ADC
relay_1 = 19
#int_outlet_1 = 19
#int_outlet_2 = 13

int_outletpins = {
        "int_outlet_1":19,
        "int_outlet_2":13,
        "int_outlet_3":6,
        "int_outlet_4":5,
        "int_outlet_5":26,
        "int_outlet_6":12,
        "int_outlet_7":16,
        "int_outlet_8":20,
    }



# MCP3008 pins
ph_adc = 0
mcp3008_ch0 = 0
mcp3008_ch1 = 1
mcp3008_ch2 = 2
mcp3008_ch3 = 3
mcp3008_ch4 = 4
mcp3008_ch5 = 5
mcp3008_ch6 = 6
mcp3008_ch7 = 7


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
    GPIO.setup(int_outletpins.get("int_outlet_1"), GPIO.OUT)
    GPIO.setup(int_outletpins.get("int_outlet_2"), GPIO.OUT)
    GPIO.setup(int_outletpins.get("int_outlet_3"), GPIO.OUT)
    GPIO.setup(int_outletpins.get("int_outlet_4"), GPIO.OUT)
    GPIO.setup(int_outletpins.get("int_outlet_5"), GPIO.OUT)
    GPIO.setup(int_outletpins.get("int_outlet_6"), GPIO.OUT)
    GPIO.setup(int_outletpins.get("int_outlet_7"), GPIO.OUT)
    GPIO.setup(int_outletpins.get("int_outlet_8"), GPIO.OUT)
