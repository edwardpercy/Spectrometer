from papirus import PapirusComposite
import time

textNImg = PapirusComposite()

# Write text to the screen at selected point, with an Id
# Nothing will show on the screen
for n in range (100):
    textNImg.AddText(f"Test {n}", 10, 10, Id="Start" )
    textNImg.UpdateText("Start", f"Test {n}")
    textNImg.WriteAll()
    time.sleep(1)