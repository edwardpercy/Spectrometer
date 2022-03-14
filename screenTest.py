from papirus import PapirusText


text = PapirusText([rotation = 90])

# Write text to the screen, in this case forty stars alternating black and white
# note the use of u"" syntax to specify unicode (needed for Python 2, optional for Python 3 since unicode is default in Python 3)
text.write(u"\u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606 \u2605 \u2606")