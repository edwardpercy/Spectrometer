#!/usr/bin/python

import spidev
import time
import struct

bus = 0
device = 1
spi = spidev.SpiDev()
spi.open(bus, device)

spi.max_speed_hz = 100000
spi.mode = 0b11

result = 0.0
cnt = 0

while(True):
	msg = 0b00
	meg = ((msg << 1) + 0) << 5
	msg = [msg, 0b00000000]
	received = spi.xfer2(msg)
	
	adc = 0
	for n in received:
		adc = (adc << 8) + n
		
	adc = adc >> 1
		
	
	if cnt >= 9:
		
		print (result/10)
		result = 0
		cnt = 0
		
		
	result += adc
	cnt += 1	

	time.sleep(0.001)
	
	
