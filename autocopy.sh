sudo mount -t vfat /dev/sda1 /media/usb
mount >> /tmp/mount.log
cd /
cd /home/pi/Desktop/Spectrometer
sudo /usr/bin/python autocopy.py
cd / 
exit