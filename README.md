# volumio-pirate-audio
Python code (plugin) to use pirate audio dac with volumio (including display and the 4 buttons) and a raspberry pi.
## Screenshots
... will follow ...
## Installation
### Clone this repository
Clone this repository to `/home/volumio/` on your raspberry pi.
````javascript
git clone https://github.com/Ax-LED/volumio-pirate-audio
````
### Set permitions/rights so files will be executable:
`sudo chmod +x /home/volumio/volumio-pirate-audio/boot.py`
`sudo chmod +x /home/volumio/ volumio-pirate-audio/display.py`
### Modifiy /boot/config.txt by adding following lines:
````javascript
### AxLED ####
dtoverlay=hifiberry-dac
gpio=25=op,dh
dtparam=spi=on
### AxLED - Fix for Button X Y of pirate audio ####
gpio=16=pu
gpio=20=pu
````
<b>Reason:</b>
- GPIO 25 settings are important for the amp
- to set PullUp of GPIO PINS 16 and 20 so they work
