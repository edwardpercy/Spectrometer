#!/usr/bin/python
import RPi.GPIO as GPIO
import spidev
import time
import struct

RELAY_PIN = 20


bus = 0
device = 1
spi = spidev.SpiDev()
spi.open(bus, device)

spi.max_speed_hz = 100000
spi.mode = 0b11

result = 0.0
cnt = 0

class StreamingMovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []
        self.sum = 0

    def process(self, value):
        self.values.append(value)
        self.sum += value
        if len(self.values) > self.window_size:
            self.sum -= self.values.pop(0)
        return float(self.sum) / len(self.values)


averageValue = StreamingMovingAverage(100)
def readADC():

	msg = 0b00
	meg = ((msg << 1) + 0) << 5
	msg = [msg, 0b00000000]
	received = spi.xfer2(msg)
	
	adc = 0
	for n in received:
		adc = (adc << 8) + n
		
	adc = adc >> 1

	return averageValue.process(adc)


GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.IN) 

while(True):
	state = GPIO.input(RELAY_PIN)
	if state == GPIO.HIGH:
		with open('output.txt', 'w') as f:
			while(GPIO.input(RELAY_PIN) == GPIO.HIGH):
				f.write(str(readADC()) + "\n")
				time.sleep(0.0001)