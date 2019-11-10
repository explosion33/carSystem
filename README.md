# carSystem

A system designed to work with raspberry pi 4 and a touch screen monitor

## Includes

  Backup Camera functionality
  
  The ability to switch between screens using a swipe
  
  Bluetooth Audio streaming from phone or other device
  
  Bluetooth commands (Play, Pause)
  
  Bluetooth Pairing
  
## Instalation
To install download the files onto a raspberry pi 4 configured with an [hdmi touchscreen](https://www.amazon.com/Elecrow-Capacitive-interface-Supports-Raspberry/dp/B07FDYXPT7/ref=asc_df_B07FDYXPT7/?tag=hyprod-20&linkCode=df0&hvadid=319216790773&hvpos=1o4&hvnetw=g&hvrand=834440554194434038&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=&hvtargid=pla-624150239484&psc=1)
then run
```python main.py```
in the terminal

## Raspberry Pi + Bluetooth Audio Setup
To setup the raspberry pi start by running
```
sudo apt-get update
```
```
sudo apt-get install bluez pulseaudio-module-bluetooth python-gobject python-gobject-2
```
then add user "pi" to the default group
```
sudo usermod -a -G lp pi
```
next enter
```
sudo nano /etc/bluetooth/audio.conf
```
and add ```Enable=Source,Sink,Media,Socket``` to the file
then enter
```
sudo nano /etc/pulse/daemon.conf
```
and add ```resample-method = trivial```
Finally Reboot, ```sudo reboot```

Change the bluetooth adapter name by entering:
```
bluetoothctl
system-alias <Alias Here>
exit
```
IF AUDIO DOES NOT PLAY MAKE SURE HEADPHONES/SPEAKERS ARE PLUGGED IN
Steps adapted from [this](https://www.raspberrypi.org/forums/viewtopic.php?t=68779) guide
