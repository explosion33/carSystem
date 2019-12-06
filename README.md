# carSystem

A system designed to work with raspberry pi 4 and a touch screen monitor

## Includes

  Backup Camera functionality
  
  The ability to switch between screens using a swipe
  
  Bluetooth Audio streaming from phone or other device
  
  Bluetooth commands (Play, Pause)
  
  Bluetooth Pairing
  
## Prerequisites

pygame ```pip3 install pygame```

numpy ```pip3 install numpy```

[opencv](https://github.com/Llibyddap/RPi_CV2) (will be installed later)
  
## Instalation
Plug in the following:

*connect ethernet (or wifi later)

*keyboard

*monitor: [hdmi touchscreen](https://www.amazon.com/Elecrow-Capacitive-interface-Supports-Raspberry/dp/B07FDYXPT7/ref=asc_df_B07FDYXPT7/?tag=hyprod-20&linkCode=df0&hvadid=319216790773&hvpos=1o4&hvnetw=g&hvrand=834440554194434038&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=&hvtargid=pla-624150239484&psc=1)



*microSD with raspbian

*usb (to migrate boot to)

*power cord

turn on the raspberrypi and continue through the setup page until it propts you to restart, do this

then run the [opencv](https://github.com/Llibyddap/RPi_CV2) script from above. This will migrate the root directory to the flashdrive and then install opencv (It will take around 3 hours to complete)

```
cd ~
git clone https://github.com/explosion33/carSystem car
cd car
python3 main.py
```

This will setup all of the graphical interfaces


## Raspberry Pi + Bluetooth Audio Setup

to setup the audio streaming portion start by entering

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

you can now pair your device in the pair menu of ```main.py``` and test for audio

IF AUDIO DOES NOT PLAY MAKE SURE HEADPHONES/SPEAKERS ARE PLUGGED IN

Steps adapted from [this](https://www.raspberrypi.org/forums/viewtopic.php?t=68779) guide
