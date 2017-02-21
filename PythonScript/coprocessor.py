#!/usr/bin/env python
# -*- coding: utf8 -*-

### Python Service for communicating with the Cypress Analog Co-Processor Pioneer Kit ###
# The objective is to read the data from the PSOC board over I2C
# and then send it via MQTT to a broker and finally to say OpenHAB etc


import RPi.GPIO as GPIO
from MFRC522 import MFRC522
import signal
import smbus
import struct
import time
import sys
import paho.mqtt.client as mqtt
import json


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("test019/coprocessor")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global _command
    #print(msg.topic+" "+str(msg.payload))
    _command=msg.payload
    print _command
        
def readCard():
    global MIFAREReader    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        #print "Card detected"
        print ''
        
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])

        if(uid[0]==185 and uid[1]==111 and uid[2]==81 and uid[3]==229 ):
            print "Welcome Inderpreet"
            
        seq=(str(uid[0]), str(uid[1]), str(uid[2]), str(uid[3]) )
        u_id='-'.join(seq)
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        #MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        #status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        #if status == MIFAREReader.MI_OK:
        #    MIFAREReader.MFRC522_Read(8)
        #    MIFAREReader.MFRC522_StopCrypto1()
        #else:
        #    print "Authentication error"
    else:
        #print "No Card Present"
        u_id='No Card'
    return u_id

def readShortReg(bus, addr, reg):
    temp =""
    temp +=chr(bus.read_byte_data(addr, reg))
    temp +=chr(bus.read_byte_data(addr, reg+1))
    number=struct.unpack('h', temp)
    return number #Returns a tuple! so use number[0] at the receiving end or modify this to meet your fancy

def motion():
    global bus
    m=bus.read_byte_data(0x08, 0)
    print m
    if(m==0x00):
        return 'OFF'
    else:
        return 'ON'

def relay_control(cmd):
    if(cmd.find('R1') >= 0 and cmd.find('ON')>0):
        #Turn On R1
        GPIO.output(11, GPIO.LOW)
        client.publish("test019/R1", "ON")
    elif(cmd.find('R1') >= 0 and cmd.find('OFF')>0):
        #Turn OFF R1
        GPIO.output(11, GPIO.HIGH)
        client.publish("test019/R1", "OFF")

    elif(cmd.find('R2') >= 0 and cmd.find('ON')>0):
        #Turn On R2
        GPIO.output(12, GPIO.LOW)
        client.publish("test019/R2", "ON")
    elif(cmd.find('R2') >= 0 and cmd.find('OFF')>0):
        #Turn OFF R2
        GPIO.output(12, GPIO.HIGH)
        client.publish("test019/R2", "OFF")

    elif(cmd.find('R3') >= 0 and cmd.find('ON')>0):
        #Turn On R3
        GPIO.output(13, GPIO.LOW)
        client.publish("test019/R3", "ON")
    elif(cmd.find('R3') >= 0 and cmd.find('OFF')>0):
        #Turn OFF R3
        GPIO.output(13, GPIO.HIGH)
        client.publish("test019/R3", "OFF")

    elif(cmd.find('R4') >= 0 and cmd.find('ON')>0):
        #Turn On R4
        GPIO.output(15, GPIO.LOW)
        client.publish("test019/R4", "ON")
    elif(cmd.find('R4') >= 0 and cmd.find('OFF')>0):
        #Turn OFF R4
        GPIO.output(15, GPIO.HIGH)
        client.publish("test019/R1", "OFF")
        
def main():
    global _motion
    global _card
    global _illu
    global _command
    count=15
    tem=0.00
    hum=0.00
    cmd=''

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    GPIO.output(11, GPIO.HIGH)
    GPIO.setup(12, GPIO.OUT)
    GPIO.output(12, GPIO.HIGH)
    GPIO.setup(13, GPIO.OUT)
    GPIO.output(13, GPIO.HIGH)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(15, GPIO.HIGH)

    GPIO.setup(36, GPIO.OUT)
    GPIO.output(36, GPIO.HIGH)
    GPIO.setup(40, GPIO.IN, GPIO.PUD_UP) #Input!!
    try:
        while True:
            m=motion()
            temp=readShortReg(bus, 0x08, 0x08)
            tem=float(temp[0])/100
            illu=readShortReg(bus, 0x08, 0x0a)
            humi=readShortReg(bus, 0x08, 0x0c)
            hum=humi[0]/10
            print temp[0]
            print illu[0]
            print humi[0]
            time.sleep(0.25) #added to make sure lines are not noisy
            u_id=readCard()
            time.sleep(0.25)
            mess=json.dumps({"motion": m, "temperature":temp[0], "illumination": illu[0], "humidity": humi[0], "uid": u_id})
            count += 1            
            if( _motion != m or _card != u_id or _illu !=illu[0] or count>=15):
                client.publish("test019/server", mess)
                client.publish("test019/server/motion", _motion)
                client.publish("test019/server/temperature", tem)
                client.publish("test019/server/illumination", illu[0])
                client.publish("test019/server/humidity", hum)
                client.publish("test019/server/uid", u_id)
                if(_card !=u_id and u_id!="No Card"):
                    time.sleep(5)
                #update variables
                _motion=m
                _card=u_id
                _illu=illu[0]
                count=0
                print "Sending Data"
            if( _command != cmd):
                relay_control(_command)
                cmd=_command
            
    except KeyboardInterrupt:
        print 'Keyboard Interrupt!'
        print 'Bye Bye!'

    finally:
        GPIO.cleanup()
        client.loop_stop()


#Lets do stuff...
_motion='OFF'
_card='No Card'
_illu=0
_command=''
bus=smbus.SMBus(1)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("iot.eclipse.org", 1883, 60)
client.loop_start()

# Capture SIGINT for cleanup when the script is aborted
#def end_read(signal,frame):
#    print "Ctrl+C captured, ending read."
#    GPIO.cleanup()
    
# Hook the SIGINT
#signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()
         
if __name__=='__main__': #ie being run directly- use else for imported as moduled
    status=main()
    sys.exit(status)
    

 
