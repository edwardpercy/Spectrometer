#!/usr/bin/python
import RPi.GPIO as GPIO
import spidev
import time
import struct

RELAY_PIN = 20
GPIO.setup(RELAY_PIN, GPIO.IN) 

bus = 0
device = 1
spi = spidev.SpiDev()
spi.open(bus, device)

spi.max_speed_hz = 100000
spi.mode = 0b11

result = 0.0
cnt = 0

def readADC():

	msg = 0b00
	meg = ((msg << 1) + 0) << 5
	msg = [msg, 0b00000000]
	received = spi.xfer2(msg)
	
	adc = 0
	for n in received:
		adc = (adc << 8) + n
		
	adc = adc >> 1

	return adc


GPIO.setmode(GPIO.BCM)

while(True):
	state = GPIO.input(RELAY_PIN)
	if state == GPIO.HIGH:
		with open('output.txt', 'w') as f:
			while(GPIO.input(RELAY_PIN) == GPIO.HIGH):
				f.write(str(readADC()) + "\n")
				time.sleep(0.001)