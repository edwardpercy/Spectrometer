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
   
import re
import subprocess
device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
df = subprocess.check_output("lsusb")
devices = []
for i in df.split('\n'):
    if i:
        info = device_re.match(i)
        if info:
            dinfo = info.groupdict()
            dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
            devices.append(dinfo)
print (devices)