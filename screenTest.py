from papirus import Papirus
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
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

draw.text((0,0), "Spectrum:", fill=BLACK, font = font)
papirus.display(image)
papirus.update()
time.sleep(1)

for x in range(0,height,4):
	draw.rectangle((x,height-x,x+2,height-x+2), fill=BLACK, outline=BLACK)
	papirus.display(image)
	papirus.partial_update()
	time.sleep(0.5)



