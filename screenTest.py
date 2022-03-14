from papirus import PapirusComposite
import time

textNImg = PapirusComposite()

# Write text to the screen at selected point, with an Id
# Nothing will show on the screen
x = 0
textNImg.AddText(str(x), 10, 10, Id="Start" )
for n in range (100):
    textNImg.UpdateText("Start", str(x))
    textNImg.WriteAll()
    time.sleep(0.5)
    x += 1