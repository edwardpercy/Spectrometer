from papirus import PapirusText

text = PapirusText([rotation = rot])

# Write text to the screen
# text.write(text)
text.write("hello world")

# Write text to the screen specifying all options
text.write(text, [size = <size> ],[fontPath = <fontpath>],[maxLines = <n>])