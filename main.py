# System imports
import RPi.GPIO as GPIO
import os
from pyudev import Context, Monitor
import multiprocessing
import shutil
import datetime
import spidev
import time
import struct
from papirus import Papirus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np

#To save model
from joblib import dump, load
import os

# Define pins
STEP_PIN = 19
DIRECTION_PIN = 13
SLEEP_PIN = 12
WHITE = 1
BLACK = 0
FONT_FILE = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
SW1 = 21
SW2 = 20
SW3 = 26
SW4 = 16

SIZE = 27

processLock = False
papirus = Papirus(rotation = 0)
papirus.clear()
image = Image.new('1', papirus.size, WHITE)
width,height = image.size
font_size = int((width - 4)/(8*1.65))
font = ImageFont.truetype(FONT_FILE, font_size)
smallFont = ImageFont.truetype(FONT_FILE, int((width - 4)/(12*1.65)))
globalResults = []
draw = ImageDraw.Draw(image)

fileimg = Image.open("homepic.bmp")
RELAY_PIN = 6 # Lamp control

bus = 0
device = 1
spi = spidev.SpiDev()
spi.open(bus, device)

spi.max_speed_hz = 100000
spi.mode = 0b11

result = 0.0
cnt = 0

classifier = load('spectro_model.joblib') 


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
	GPIO.output(SLEEP_PIN, GPIO.LOW)
	#stepperHandler.home()

def read_text_file(file_path):
    with open(file_path, 'r') as f:
        temp = []
        for line in f:
            temp.append(float(line))
        x = temp
    
    Datalen = len(x)
 
    combLength = Datalen - 141999
    combDist = (Datalen / combLength)

    for t in range (combLength-1, 0,-1):
        x.pop(round(t * combDist))
       
    
    x = normalise(x)
    print("Data normalised")  

    x = np.array(x)
    x = x.astype(float)

    return x
        

        
def normalise(input):
    output = input
    count = 0
    minval = min(input)
    maxval = max(input)
    for x in range (len(input)):
        count += 1
        output[x] = (input[x]-minval)/(maxval-minval)
 
    return output

def capture_routine():
	global globalResults

	
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


	data = read_text_file("output.txt")
	y_pred = classifier.predict(data)
	y_pred = int(y_pred.data[0]) - 1
	print(y_pred)
	vals = ["Blue", "Canal", "Distilled", "Green","Red"]
	print(vals[y_pred])


	draw.text((((width/2) - (9*11)),30), vals[y_pred], fill=BLACK, font = font)
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
		adjR = ((height-40) - (r * (height-40))) + (20)
		draw.rectangle((xVal,adjR,xVal-1,adjR-1), fill=BLACK, outline=BLACK)
		xVal += 1

	draw.rectangle((0, height-12,width, height-13), fill=BLACK, outline=BLACK)
	draw.text((0,height-10), "300", fill=BLACK, font = smallFont)
	draw.rectangle((9*2, height-10,(9*2)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*3,height-10), "400", fill=BLACK, font = smallFont)
	draw.rectangle((9*5, height-10,(9*5)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*6,height-10), "500", fill=BLACK, font = smallFont)
	draw.rectangle((9*8, height-10,(9*8)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*9,height-10), "600", fill=BLACK, font = smallFont)
	draw.rectangle((9*11, height-10,(9*11)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*12,height-10), "700", fill=BLACK, font = smallFont)
	draw.rectangle((9*14, height-10,(9*14)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*15,height-10), "800", fill=BLACK, font = smallFont)
	draw.rectangle((9*17, height-10,(9*17)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*18,height-10), "900", fill=BLACK, font = smallFont)
	draw.rectangle((9*20, height-10,(9*20)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*21,height-10), "1000", fill=BLACK, font = smallFont)
	draw.rectangle((9*24, height-10,(9*24)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*25,height-10), "1100", fill=BLACK, font = smallFont)
	
	papirus.display(image)
	papirus.update()

def usb():
	papirus.clear()
	draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
	draw.text((((width/2) - (9*11)),0), "Insert USB Device.", fill=BLACK, font = font)

	papirus.display(image)
	papirus.update()

	disks = []
	while(len(disks) <= 0):
		context = Context()
		for device in context.list_devices(subsystem="block"):
			if device.device_type == u"disk":
				property_dict = dict(device.items())

				if ('ID_MODEL' in property_dict):
					disk_short_name = property_dict.get('DEVNAME', "Unknown").split('/')[-1]
					disks.append(
					{
						'model':	property_dict.get('ID_MODEL', "Unknown"),
						'name':		disk_short_name,
						'serial':	property_dict.get('ID_SERIAL_SHORT', "Unknown"),
					})

	papirus.clear()
	draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
	lenDisks = len(disks)
	if (lenDisks >= 1) : draw.text((33,0), "1", fill=BLACK, font = font)
	draw.rectangle((60, 0, 61, 20), fill=BLACK, outline=BLACK)
	if (lenDisks >= 2) : draw.text((88,0), "2", fill=BLACK, font = font)
	draw.rectangle((115, 0, 116, 20), fill=BLACK, outline=BLACK)
	if (lenDisks >= 3) : draw.text((136,0), "3", fill=BLACK, font = font)
	draw.rectangle((160, 0, 161, 20), fill=BLACK, outline=BLACK)
	if (lenDisks >= 4) : draw.text((200,0), "4", fill=BLACK, font = font)
	draw.rectangle((0, 20,width, height), fill=WHITE, outline=BLACK)

	draw.text((((width/2) - (5*11)),40), "Select USB", fill=BLACK, font = font)
	count = 1
	for d in disks:
		disktext = str(f"{str(count)}: {str(d['model'])}")
		draw.text((0,80), disktext, fill=BLACK, font = font)
		count += 1

	papirus.display(image)
	papirus.update()
	selDisk = ""
	while(True):
		if GPIO.input(SW1) == False and (lenDisks >= 1):
			draw.rectangle((0, 0, 60, 20), fill=BLACK, outline=BLACK)
			draw.text((33,0), "1", fill=BLACK, font = font)
			draw.rectangle((61, 0, 115, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((116, 0, 160, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((161, 0, width, 20), fill=WHITE, outline=BLACK)
			selDisk = disks[0]['name']
			papirus.display(image)
			papirus.partial_update()
			break
		elif GPIO.input(SW2) == False and (lenDisks >= 2):
			draw.rectangle((61, 0, 115, 20), fill=BLACK, outline=BLACK)
			draw.rectangle((0, 0, 60, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((116, 0, 160, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((161, 0, width, 20), fill=WHITE, outline=BLACK)
			draw.text((88,0), "2", fill=BLACK, font = font)
			selDisk = disks[1]['name']
			papirus.display(image)
			papirus.partial_update()
			break
		elif GPIO.input(SW3) == False and (lenDisks >= 3):
			draw.rectangle((116, 0, 160, 20), fill=BLACK, outline=BLACK)
			draw.rectangle((61, 0, 115, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((0, 0, 60, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((161, 0, width, 20), fill=WHITE, outline=BLACK)
			draw.text((136,0), "3", fill=BLACK, font = font)
			selDisk = disks[2]['name']
			papirus.display(image)
			papirus.partial_update()
			break
		elif GPIO.input(SW4) == False and (lenDisks >= 4):
			draw.rectangle((161, 0, width, 20), fill=BLACK, outline=BLACK)
			draw.rectangle((61, 0, 115, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((116, 0, 160, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((0, 0, 60, 20), fill=WHITE, outline=BLACK)
			draw.text((200,0), "4", fill=BLACK, font = font)
			selDisk = disks[3]['name']
			papirus.display(image)
			papirus.partial_update()
			break

	papirus.clear()
	draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
	papirus.display(image)
	papirus.update()

	draw.text((((width/2) - (6*11)),20), "Mounting USB", fill=BLACK, font = font)
	papirus.display(image)
	papirus.partial_update()

	os.system(f"sudo mount /dev/{selDisk}1 /media/usb") 
	draw.text((((width/2) - (5*11)),45), "Mounted...", fill=BLACK, font = font)
	papirus.display(image)
	papirus.partial_update()

	draw.text((((width/2) - (10*11)),70), "Writing data to USB.", fill=BLACK, font = font)
	papirus.display(image)
	papirus.partial_update()

	# File to be copied
	source = "/home/pi/Desktop/Spectrometer/output.txt"

	# USB name must be changed to 'USB1' in order for auto copy to work
	destination = "/media/usb/datalogger_backup_%s.txt" % datetime.datetime.now().date()

	try:
		# Copy file to destination
		shutil.copyfile(source, destination)
		# E.g. source and destination is the same location
	except shutil.Error as e:
		print("Error: %s" % e)
		# E.g. source or destination does not exist
	except IOError as e:
		print("Error: %s" % e.strerror)

	draw.text((((width/2) - (4*11)),95), "Success.", fill=BLACK, font = font)
	papirus.display(image)
	papirus.partial_update()

	draw.text((((width/2) - (8*11)),120), "Un-Mounting USB.", fill=BLACK, font = font)
	papirus.display(image)
	papirus.partial_update()

	os.system("sudo umount /media/usb")

	draw.text((((width/2) - (7*11)),145), "Safe to Eject.", fill=BLACK, font = font)
	papirus.display(image)
	papirus.partial_update()
	time.sleep(1)
	papirus.clear()
	draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
	draw.text((11,0), "Scan", fill=BLACK, font = font)
	draw.rectangle((60, 0, 61, 20), fill=BLACK, outline=BLACK)
	draw.text((66,0), "Data", fill=BLACK, font = font)
	draw.rectangle((115, 0, 116, 20), fill=BLACK, outline=BLACK)
	draw.text((121,0), "USB", fill=BLACK, font = font)
	draw.rectangle((160, 0, 161, 20), fill=BLACK, outline=BLACK)
	draw.text((165,0), "Options", fill=BLACK, font = font)
	draw.rectangle((0, 20,width, height), fill=BLACK, outline=BLACK)
	image.paste(fileimg, (25, 40))
	papirus.display(image)
	papirus.update()


def scan():
	papirus.clear()
	draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
	draw.text((((width/2) - (9*11)),0), "Photo Spectrometry", fill=BLACK, font = font)

	papirus.display(image)
	papirus.update()

	draw.text((((width/2) - (7*11)),20), "Homing Stepper", fill=BLACK, font = font)
	papirus.display(image)
	papirus.partial_update()

	GPIO.output(SLEEP_PIN, GPIO.HIGH)
	# Create a new instance of our stepper class (note if you're just starting out with this you're probably better off using a delay of ~0.1)
	
	stepperHandler.Step(100, stepperHandler.ANTI_CLOCKWISE)
	stepperHandler.home()


	draw.text((((width/2) - (6*11)),60), "Scanning ...", fill=BLACK, font = font)
	papirus.display(image)
	papirus.partial_update()

	# Go backwards once
	GPIO.output(RELAY_PIN, GPIO.HIGH)

	captureProcess = multiprocessing.Process(target=capture_routine, args=())
	stepperProcess = multiprocessing.Process(target=stepper_routine, args=())
	processLock == True
	captureProcess.start()
	stepperProcess.start()

	captureProcess.join()
	stepperProcess.join()

	while (True):
		if (processLock == False):
			papirus.clear()
			draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
			draw.text((11,0), "Scan", fill=BLACK, font = font)
			draw.rectangle((60, 0, 61, 20), fill=BLACK, outline=BLACK)
			draw.text((66,0), "Data", fill=BLACK, font = font)
			draw.rectangle((115, 0, 116, 20), fill=BLACK, outline=BLACK)
			draw.text((121,0), "USB", fill=BLACK, font = font)
			draw.rectangle((160, 0, 161, 20), fill=BLACK, outline=BLACK)
			draw.text((165,0), "Options", fill=BLACK, font = font)
			draw.rectangle((0, 20,width, height), fill=BLACK, outline=BLACK)
			image.paste(fileimg, (35, 40))
			papirus.display(image)
			papirus.update()
			break
		
	

def write_text(papirus, text, size):

    # initially set all white background
    image = Image.new('1', papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', size)

    # Calculate the max number of char to fit on line
    line_size = (papirus.width / (size*0.65))

    current_line = 0
    text_lines = [""]

    # Compute each line
    for word in text.split():
        # If there is space on line add the word to it
        if (len(text_lines[current_line]) + len(word)) < line_size:
            text_lines[current_line] += " " + word
        else:
            # No space left on line so move to next one
            text_lines.append("")
            current_line += 1
            text_lines[current_line] += " " + word

    current_line = 0
    for l in text_lines:
        current_line += 1
        draw.text( (0, ((size*current_line)-size)) , l, font=font, fill=BLACK)

    papirus.display(image)
    papirus.partial_update()

def data():
	
	pastResults = loadPrevResults()

	temp = []
	count = 0
	for res in range(len(pastResults)):
		if (count % 500 == 0):
			temp.append(pastResults[res])
		count+=1


	papirus.clear()
	draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
	draw.text((11,0), "Exit", fill=BLACK, font = font)
	draw.rectangle((60, 0, 61, 20), fill=BLACK, outline=BLACK)


	
	draw.text((((width/2) - (6*11)),0), "Spectral Results", fill=BLACK, font = font)

	if (len(temp) > width):
		for x in range(len(temp) - width):
			del temp[-x]
	elif (len(temp) < width):
		for x in range(width - len(temp)):
			temp.append(0)
	
	normResults = normalise(temp)

	xVal = 0
	for r in normResults:
		adjR = ((height-40) - (r * (height-40))) + (20)
		draw.rectangle((xVal,adjR,xVal-1,adjR-1), fill=BLACK, outline=BLACK)
		xVal += 1
	
	draw.rectangle((0, height-12,width, height-13), fill=BLACK, outline=BLACK)
	draw.text((0,height-10), "400", fill=BLACK, font = smallFont)
	draw.rectangle((9*2, height-10,(9*2)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*3,height-10), "500", fill=BLACK, font = smallFont)
	draw.rectangle((9*5, height-10,(9*5)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*6,height-10), "600", fill=BLACK, font = smallFont)
	draw.rectangle((9*8, height-10,(9*8)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*9,height-10), "700", fill=BLACK, font = smallFont)
	draw.rectangle((9*11, height-10,(9*11)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*12,height-10), "800", fill=BLACK, font = smallFont)
	draw.rectangle((9*14, height-10,(9*14)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*15,height-10), "900", fill=BLACK, font = smallFont)
	draw.rectangle((9*17, height-10,(9*17)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*18,height-10), "1000", fill=BLACK, font = smallFont)
	draw.rectangle((9*20, height-10,(9*20)+1, height-15), fill=BLACK, outline=BLACK)
	draw.text((9*23,height-10), "1100", fill=BLACK, font = smallFont)
	draw.rectangle((9*24, height-10,(9*24)+1, height-15), fill=BLACK, outline=BLACK)

	



	papirus.display(image)
	papirus.update()

	while(True):
		if GPIO.input(SW1) == False:
			draw.rectangle((0, 0, 60, 20), fill=BLACK, outline=BLACK)
			draw.text((11,0), "Exit", fill=BLACK, font = font)
			draw.rectangle((61, 0, 115, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((116, 0, 160, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((161, 0, width, 20), fill=WHITE, outline=BLACK)
			papirus.display(image)
			papirus.partial_update()
			break

	papirus.clear()
	draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
	draw.text((11,0), "Scan", fill=BLACK, font = font)
	draw.rectangle((60, 0, 61, 20), fill=BLACK, outline=BLACK)
	draw.text((66,0), "Data", fill=BLACK, font = font)
	draw.rectangle((115, 0, 116, 20), fill=BLACK, outline=BLACK)
	draw.text((121,0), "USB", fill=BLACK, font = font)
	draw.rectangle((160, 0, 161, 20), fill=BLACK, outline=BLACK)
	draw.text((165,0), "Options", fill=BLACK, font = font)
	draw.rectangle((0, 20,width, height), fill=BLACK, outline=BLACK)
	image.paste(fileimg, (35, 40))
	papirus.display(image)
	papirus.update()

def menu():
	
	papirus.clear()
	draw.rectangle((0, 0, width, height), fill=WHITE, outline=BLACK)
	draw.text((11,0), "Scan", fill=BLACK, font = font)
	draw.rectangle((60, 0, 61, 20), fill=BLACK, outline=BLACK)
	draw.text((66,0), "Data", fill=BLACK, font = font)
	draw.rectangle((115, 0, 116, 20), fill=BLACK, outline=BLACK)
	draw.text((121,0), "USB", fill=BLACK, font = font)
	draw.rectangle((160, 0, 161, 20), fill=BLACK, outline=BLACK)
	draw.text((165,0), "Options", fill=BLACK, font = font)
	draw.rectangle((0, 20,width, height), fill=BLACK, outline=BLACK)
	image.paste(fileimg, (35, 40))
	papirus.display(image)
	papirus.update()

	while(True):
		if GPIO.input(SW1) == False:
			draw.rectangle((0, 0, 60, 20), fill=BLACK, outline=BLACK)
			draw.text((11,0), "Scan", fill=BLACK, font = font)
			draw.rectangle((61, 0, 115, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((116, 0, 160, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((161, 0, width, 20), fill=WHITE, outline=BLACK)
			papirus.display(image)
			papirus.partial_update()
			scan()
		if GPIO.input(SW2) == False:
			draw.rectangle((61, 0, 115, 20), fill=BLACK, outline=BLACK)
			draw.rectangle((0, 0, 60, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((116, 0, 160, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((161, 0, width, 20), fill=WHITE, outline=BLACK)
			draw.text((66,0), "Data", fill=BLACK, font = font)
			papirus.display(image)
			papirus.partial_update()
			data()
		if GPIO.input(SW3) == False:
			draw.rectangle((116, 0, 160, 20), fill=BLACK, outline=BLACK)
			draw.rectangle((61, 0, 115, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((0, 0, 60, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((161, 0, width, 20), fill=WHITE, outline=BLACK)
			draw.text((121,0), "USB", fill=BLACK, font = font)
			papirus.display(image)
			papirus.partial_update()
			usb()
		if GPIO.input(SW4) == False:
			draw.rectangle((161, 0, width, 20), fill=BLACK, outline=BLACK)
			draw.rectangle((61, 0, 115, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((116, 0, 160, 20), fill=WHITE, outline=BLACK)
			draw.rectangle((0, 0, 60, 20), fill=WHITE, outline=BLACK)
			draw.text((165,0), "Options", fill=BLACK, font = font)
			papirus.display(image)
			papirus.partial_update()

def loadPrevResults():
	global globalResults
	with open('output.txt') as f:
		outLines = f.readlines()
	count = 0
	for line in outLines:
		if (count % 500 == 0):
			globalResults.append(float(line))
		count += 1

	return globalResults

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(SLEEP_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)
GPIO.output(SLEEP_PIN, GPIO.LOW)
GPIO.setup(SW1, GPIO.IN)
GPIO.setup(SW2, GPIO.IN)
GPIO.setup(SW3, GPIO.IN)
GPIO.setup(SW4, GPIO.IN)

stepperHandler = StepperHandler(STEP_PIN, DIRECTION_PIN, 0.01)
loadPrevResults()
menu()


