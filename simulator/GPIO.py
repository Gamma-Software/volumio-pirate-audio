
BCM = 0
IN = 0
PUD_UP = 0
FALLING = 0

buttons = {"5": 0, "6": 0, "16": 0, "20": 0}

def setmode(mode):
    print("setmode Not implemented on simulator")

def cleanup(button):
    print("cleanup Not implemented on simulator")

def setup(channel, pin, direction):
    print("setup Not implemented on simulator")

def press_key(pin):
    buttons[str(pin)] = 1
    callback(pin) # Call the callback function only if the button is pressed

def release_key(pin):
    buttons[str(pin)] = 0

def add_event_detect(pin_channels, direction, _callback, bouncetime):
    global callback
    callback = _callback

def input(pin):
    ret = buttons[str(pin)]
    if ret != 0:
        release_key(pin)
    return not bool(ret)
