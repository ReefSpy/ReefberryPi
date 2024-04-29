from gpiozero import MCP3008

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    
    dv = int(MCP3008(channel = adcnum, 
            clock_pin = clockpin, 
            mosi_pin = mosipin, 
            miso_pin = misopin, 
            select_pin = cspin).value * 1023)

    return dv







# import RPi.GPIO as GPIO

# # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
# def readadc(adcnum, clockpin, mosipin, misopin, cspin):
#         if ((adcnum > 7) or (adcnum < 0)):
#                 return -1
#         GPIO.output(cspin, True)

#         GPIO.output(clockpin, False)  # start clock low
#         GPIO.output(cspin, False)     # bring CS low

#         commandout = adcnum
#         commandout |= 0x18  # start bit + single-ended bit
#         commandout <<= 3    # we only need to send 5 bits here
#         for i in range(5):
#                 if (commandout & 0x80):
#                         GPIO.output(mosipin, True)
#                 else:
#                         GPIO.output(mosipin, False)
#                 commandout <<= 1
#                 GPIO.output(clockpin, True)
#                 GPIO.output(clockpin, False)

#         adcout = 0
#         # read in one empty bit, one null bit and 10 ADC bits
#         for i in range(12):
#                 GPIO.output(clockpin, True)
#                 GPIO.output(clockpin, False)
#                 adcout <<= 1
#                 if (GPIO.input(misopin)):
#                         adcout |= 0x1

#         GPIO.output(cspin, True)
        
#         adcout >>= 1       # first bit is 'null' so drop it
#         return adcout
