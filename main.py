# System imports
import RPi.GPIO as GPIO
import os

import multiprocessing

import spidev
import time
import struct
from papirus import Papirus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np

# Define pins
STEP_PIN = 19
DIRECTION_PIN = 13
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
# Lamp control
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
    minVal = min(input)
    maxVal = max(input)
    
    for x in range (len(input)):
        output[x] = (input[x]-minVal) / (maxVal-minVal)
	# output = output/np.linalg.norm(output)

	#output = moving_average(output, n=10)
    return output
    

averageValue = StreamingMovingAverage(500)
sampleSpeed = 0.000001

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

class StepperHandler():

	__CLOCKWISE = 1
	__ANTI_CLOCKWISE = 0

	def __init__(self, stepPin, directionPin, delay=0.208, stepsPerRevolution=200):
		# Configure instance
		self.CLOCKWISE = self.__CLOCKWISE
		self.ANTI_CLOCKWISE = self.__ANTI_CLOCKWISE
		self.StepPin = stepPin
		self.SwitchPin = 5
		self.DirectionPin = directionPin
		self.Delay = delay
		self.RevolutionSteps = stepsPerRevolution
		self.CurrentDirection = self.CLOCKWISE
		self.CurrentStep = 0

		# Setup gpio pins
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.StepPin, GPIO.OUT)
		GPIO.setup(self.DirectionPin, GPIO.OUT)
		GPIO.setup(self.SwitchPin, GPIO.IN)

	def Step(self, stepsToTake, direction = __CLOCKWISE):

		# Set the direction
		GPIO.output(self.DirectionPin, direction)

		# Take requested number of steps
		for x in range(stepsToTake):
			if (GPIO.input(self.SwitchPin) == GPIO.HIGH or direction == self.ANTI_CLOCKWISE):
				GPIO.output(self.StepPin, GPIO.HIGH)
				self.CurrentStep += 1
				time.sleep(self.Delay)
				GPIO.output(self.StepPin, GPIO.LOW)
				time.sleep(self.Delay)
			
	def home(self, direction = __CLOCKWISE):
	
		# Set the direction
		GPIO.output(self.DirectionPin, direction)

		

		# Take requested number of steps
		while (GPIO.input(self.SwitchPin) == GPIO.HIGH):
			GPIO.output(self.StepPin, GPIO.HIGH)
			self.CurrentStep += 1
			time.sleep(self.Delay)
			GPIO.output(self.StepPin, GPIO.LOW)
			time.sleep(self.Delay)
		stepperHandler.Step(10, stepperHandler.ANTI_CLOCKWISE)

def stepper_routine():
	stepperHandler.Step(2600, stepperHandler.ANTI_CLOCKWISE)
	GPIO.output(RELAY_PIN, GPIO.LOW)
	stepperHandler.Step(2000, stepperHandler.CLOCKWISE)
	#stepperHandler.home()


def capture_routine():
	count = 0
	results = []

	with open('output.txt', 'w') as f:
		#time.sleep(1.3)
		while(GPIO.input(RELAY_PIN) == GPIO.HIGH):
			val = readADC()
			f.write(str(val) + "\n")
			time.sleep(sampleSpeed)
			count += 1
			if (count % 500 == 0):
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
		adjR = ((height-40) - (r * (height-40))) + (40)
		draw.rectangle((xVal,adjR,xVal-1,adjR-1), fill=BLACK, outline=BLACK)
		xVal += 1
	
	papirus.display(image)
	papirus.update()


GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)


draw.text((((width/2) - (9*11)),0), "Photo Spectrometry", fill=BLACK, font = font)

papirus.display(image)
papirus.update()

draw.text((((width/2) - (7*11)),20), "Homing Stepper", fill=BLACK, font = font)
papirus.display(image)
papirus.partial_update()

# Create a new instance of our stepper class (note if you're just starting out with this you're probably better off using a delay of ~0.1)
stepperHandler = StepperHandler(STEP_PIN, DIRECTION_PIN, 0.01)
stepperHandler.Step(100, stepperHandler.ANTI_CLOCKWISE)
stepperHandler.home()


draw.text((((width/2) - (6*11)),60), "Scanning ...", fill=BLACK, font = font)
papirus.display(image)
papirus.partial_update()

# Go backwards once
GPIO.output(RELAY_PIN, GPIO.HIGH)

captureProcess = multiprocessing.Process(target=capture_routine, args=())
stepperProcess = multiprocessing.Process(target=stepper_routine, args=())

captureProcess.start()
stepperProcess.start()

captureProcess.join()
stepperProcess.join()

