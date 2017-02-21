import smbus
import time

bus=smbus.SMBus(1)

while True:
    print "checking..."
    bus.write_byte_data(0x08, 0, 0)
    mot=bus.read_byte_data(0x08, 0)
    print mot
    time.sleep(0.5)
