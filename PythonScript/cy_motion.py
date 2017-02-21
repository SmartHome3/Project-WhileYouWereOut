import smbus
import time
import sys
import struct

bus=smbus.SMBus(1)

def readShortReg(bus, addr, reg):
    temp =""
    temp +=chr(bus.read_byte_data(addr, reg))
    temp +=chr(bus.read_byte_data(addr, reg+1))
    number=struct.unpack('h', temp)
    return number

def motion():
    global bus
    m = bus.read_byte_data(0x08, 0)
    print m
    temp=readShortReg(bus, 0x08, 0x08)
    print temp
    

def main():
    try:
        while True:
            motion()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print 'Keyboard Interrupt!'
        print 'Bye Bye!'
        return 0
        
if __name__=='__main__': #ie being run directly- use else for imported as moduled
    status=main()
    sys.exit(status)
    


