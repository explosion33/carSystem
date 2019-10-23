# carSystem

A system designed to work with raspberry pi 4 and a touch screen monitor

It currently includes:
  Backup Camera functionality
  The ability to switch between screens using a swipe
  
## Instalation
To install download the files onto a raspberry pi 4 configured with an [hdmi touchscreen](https://www.amazon.com/Elecrow-Capacitive-interface-Supports-Raspberry/dp/B07FDYXPT7/ref=asc_df_B07FDYXPT7/?tag=hyprod-20&linkCode=df0&hvadid=319216790773&hvpos=1o4&hvnetw=g&hvrand=834440554194434038&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=&hvtargid=pla-624150239484&psc=1)
then run
```python main.py```
in the terminal

## Raspberry Pi + Bluetooth Audio Setup
To setup the raspberry pi start by running\n
```sudo apt-get update```\n
```sudo apt-get install bluez pulseaudio-module-bluetooth python-gobject python-gobject-2```\n
then add user "pi" to the default group\n
```sudo usermod -a -G lp pi```\n
next enter\n
```sudo nano /etc/bluetooth/audio.conf```\n
and add ```Enable=Source,Sink,Media,Socket``` to the file\n
then enter\n
```sudo nano /etc/pulse/daemon.conf```\n
and add ```resample-method = trivial```\n
Finally Reboot, ```sudo reboot```\n

Change the bluetooth adapter name by entering:
```
bluetoothctl
system-alias <Alias Here>
```
Steps adapted from this[https://www.raspberrypi.org/forums/viewtopic.php?t=68779] guide
