import smbus
import time


bus=smbus.SMBus(1)

while True:
    temp=bus.read_byte_data(0x08, 0)
    print temp
    time.sleep(1)
    
