#!/usr/bin/python
import RPi.GPIO as GPIO
import spidev
import time
import struct
from papirus import Papirus
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np


WHITE = 1
BLACK = 0
FONT_FILE = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'

papirus = Papirus(rotation = 0)
papirus.clear()
image = Image.new('1', papirus.size, WHITE)
width,height = image.size
font_size = int((width - 4)/(8*1.65))
font = ImageFont.truetype(FONT_FILE, font_size)

draw = ImageDraw.Draw(image)

RELAY_PIN = 6



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

def normalise(input):
	output = input
	for x in range (len(input)):
		output[x] = (input[x]-min(input))/(max(input)-min(input))
	# output = output/np.linalg.norm(output)

	#output = moving_average(output, n=10)
	return output

averageValue = StreamingMovingAverage(500)
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


draw.text((((width/2) - (9*11)),0), "Photo Spectrometry", fill=BLACK, font = font)

papirus.display(image)
papirus.update()

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.IN) 

exitFlag = False
while(exitFlag == False):

	if GPIO.input(RELAY_PIN) == GPIO.HIGH:
		exitFlag = True
		count = 0
		results = []
		draw.text((((width/2) - (6*11)),20), "Scanning ...", fill=BLACK, font = font)
		papirus.display(image)
		papirus.partial_update()

		with open('output.txt', 'w') as f:
			#time.sleep(1.3)
			while(GPIO.input(RELAY_PIN) == GPIO.HIGH):
				val = readADC()
				f.write(str(val) + "\n")
				time.sleep(0.0001)
				count += 1
				if (count % 250 == 0):
					results.append(val)

	
		papirus.clear()
		draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
		papirus.update()
		
		draw.text((((width/2) - (9*11)),8), "Spectral Results", fill=BLACK, font = font)

		if (len(results) > width):
			for x in range(len(results) - width):
				del results[-x]
		elif (len(results) < width):
			for x in range(width - len(results)):
				results.append(0)

		
		normResults = normalise(results)

		xVal = 0
		for r in normResults:
			adjR = (height+ (11*8)) - (r * height)
			draw.rectangle((xVal,adjR,xVal+1,adjR+1), fill=BLACK, outline=BLACK)
			xVal += 1
		
		papirus.display(image)
		papirus.partial_update()