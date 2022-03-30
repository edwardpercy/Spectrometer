# System imports
import RPi.GPIO as GPIO
import os
from time import sleep

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
				sleep(self.Delay)
				GPIO.output(self.StepPin, GPIO.LOW)
				sleep(self.Delay)
			
	def home(self, direction = __CLOCKWISE):
	
		# Set the direction
		GPIO.output(self.DirectionPin, direction)

		

		# Take requested number of steps
		while (GPIO.input(self.SwitchPin) == GPIO.HIGH):
			GPIO.output(self.StepPin, GPIO.HIGH)
			self.CurrentStep += 1
			sleep(self.Delay)
			GPIO.output(self.StepPin, GPIO.LOW)
			sleep(self.Delay)
		stepperHandler.Step(10, stepperHandler.ANTI_CLOCKWISE)

# Define pins
STEP_PIN = 19
DIRECTION_PIN = 13

# Lamp control
RELAY_PIN = 6

# Create a new instance of our stepper class (note if you're just starting out with this you're probably better off using a delay of ~0.1)
stepperHandler = StepperHandler(STEP_PIN, DIRECTION_PIN, 0.01)
stepperHandler.Step(100, stepperHandler.ANTI_CLOCKWISE)
stepperHandler.home()

os.system('./launch.sh')
sleep(2)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

sleep(6)
# Go backwards once
GPIO.output(RELAY_PIN, GPIO.HIGH)

stepperHandler.Step(1300, stepperHandler.ANTI_CLOCKWISE)
GPIO.output(RELAY_PIN, GPIO.LOW)

stepperHandler.home()

# Go forwards once (Towards Motor)
#GPIO.output(RELAY_PIN, GPIO.HIGH)
#stepperHandler.Step(1000)
#GPIO.output(RELAY_PIN, GPIO.LOW)


# Go forwards once (Towards Motor)dsa
#stepperHandler.Step(400)


