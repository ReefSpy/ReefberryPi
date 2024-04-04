import GPIO_config
import Adafruit_DHT as dht

class DHT22:  
    def read():
        try:
            DHT = GPIO_config.dht22
            #Read Temp and Hum from DHT22
            h,t = dht.read_retry(dht.DHT22, DHT)
            #Print Temperature and Humidity on Shell window
            # print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(t,h))
            h = '{0:0.1f}'.format(h)
            t = '{0:0.1f}'.format(t)
            return (h, t)
        except Exception as e:
            print(e)




