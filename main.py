# System imports
import RPi.GPIO as GPIO
from time import sleep
import spidev
import time
import struct

bus = 0
device = 0
spi = spidev.SpiDev()
spi.open(bus, device)

spi.max_speed_hz = 1000
spi.mode = 0b11

currResult = 0.0
result = 0.0
cnt = 0

def readADC():
	global currResult
	
	total = 0
	
	for x in range(3):
		msg = 0b00
		meg = ((msg << 1) + 0) << 5
		msg = [msg, 0b00000000]
		received = spi.xfer2(msg)
		
		adc = 0
		for n in received:
			adc = (adc << 8) + n
			
		adc = adc >> 1
		total += adc
	currResult = total/3
	# if cnt >= 9:
		
	# 	currResult = result/10
	# 	result = 0
	# 	cnt = 0
		
		
	# result += adc
	# cnt += 1	

class StepperHandler():

	__CLOCKWISE = 1
	__ANTI_CLOCKWISE = 0

	def __init__(self, stepPin, directionPin, delay=0.208, stepsPerRevolution=200):
		# Configure instance
		self.CLOCKWISE = self.__CLOCKWISE
		self.ANTI_CLOCKWISE = self.__ANTI_CLOCKWISE
		self.StepPin = stepPin
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

	def Step(self, stepsToTake, direction = __CLOCKWISE):
		global currResult

		print("Step Pin: " + str(self.StepPin) + " Direction Pin: " + str(self.DirectionPin) + " Delay: " + str(self.Delay))
		print("Taking " + str(stepsToTake) + " steps.")

		# Set the direction
		GPIO.output(self.DirectionPin, direction)

		if (direction == self.CLOCKWISE):
			# Take requested number of steps
			with open('output.txt', 'w') as f:
				for x in range(stepsToTake):
					readADC()
					print("Step " + str(x) + "ADC " + str(currResult))
					f.write(str(currResult) + "\n")
					GPIO.output(self.StepPin, GPIO.HIGH)
					self.CurrentStep += 1
					sleep(self.Delay)
					GPIO.output(self.StepPin, GPIO.LOW)
					sleep(self.Delay)
		else:
			for x in range(stepsToTake):
					print("Step " + str(x))
					GPIO.output(self.StepPin, GPIO.HIGH)
					self.CurrentStep += 1
					sleep(self.Delay)
					GPIO.output(self.StepPin, GPIO.LOW)
					sleep(self.Delay)

# Define pins
STEP_PIN = 16
DIRECTION_PIN = 21

# Lamp control
RELAY_PIN = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

# Create a new instance of our stepper class (note if you're just starting out with this you're probably better off using a delay of ~0.1)
stepperHandler = StepperHandler(STEP_PIN, DIRECTION_PIN, 0.01)

# Go forwards once (Towards Motor)
GPIO.output(RELAY_PIN, GPIO.HIGH)
stepperHandler.Step(1000)
GPIO.output(RELAY_PIN, GPIO.LOW)

# Go backwards once
stepperHandler.Step(1000, stepperHandler.ANTI_CLOCKWISE)

# Go forwards once (Towards Motor)dsa
#stepperHandler.Step(400)


for x in range (2):
	GPIO.output(RELAY_PIN, GPIO.LOW)
	sleep(1)
	#GPIO.output(RELAY_PIN, GPIO.HIGH)
	sleep(1)
GPIO.output(RELAY_PIN, GPIO.LOW)



