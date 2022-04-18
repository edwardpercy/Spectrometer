# import shutil
# import datetime

# # File to be copied
# source = "/home/pi/Desktop/Spectrometer/output.txt"

# # USB name must be changed to 'USB1' in order for auto copy to work
# destination = "/media/pi/USB1/datalogger_backup_%s.txt" % datetime.datetime.now().date()

# try:
   # # Copy file to destination
   # shutil.copy2(source, destination)
   # # E.g. source and destination is the same location
# except shutil.Error as e:
   # print("Error: %s" % e)
   # # E.g. source or destination does not exist
# except IOError as e:
   # print("Error: %s" % e.strerror)
   
#!/usr/bin/env python
import os
import subprocess

rpistr = "ls /media/pi"
proc = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid,stdout=subprocess.PIPE)
line = proc.stdout.readline()
print (line.rstrip())