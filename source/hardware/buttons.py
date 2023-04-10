import time

from source import SIMULATOR
if SIMULATOR:
    from source.simulator.gpio import GPIOSingleton  # simulator
    GPIO = GPIOSingleton()
else:
    import RPi.GPIO as GPIO


class ButtonHandler:
    def __init__(self, button_mapping) -> None:
        self.button_mapping = button_mapping
        self.callbacks = []
        GPIO.setmode(GPIO.BCM)

        # Setup GPIO pins
        try:
            for pin in self.button_mapping.values():
                GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)
                GPIO.add_event_detect(pin, GPIO.FALLING, self.handle_button, bouncetime=500)
                time.sleep(0.1)  # Wait a bit
        except (ValueError, RuntimeError) as e:
            print('ERROR at setup channel:', e)

    def remove_all_listers(self):
        self.callbacks = []

    def add_callbacks(self, callback, priority=0):
        if callback in self.callbacks:
            return
        if priority == 0:
            self.callbacks.insert(0, callback)
        else:
            self.callbacks.append(callback)

    def remove_callbacks(self, callback):
        self.callbacks.remove(callback)

    def clean(self):
        GPIO.cleanup(list(self.button_mapping.values()))

    def handle_button(self, pin):
        print('Button pressed: ', pin)
        # Avoid the fact that the callback list may change during the loop
        current_callbacks = self.callbacks.copy()
        for call in current_callbacks:
            key = list(self.button_mapping.keys())[
                list(self.button_mapping.values()).index(pin)]
            call(key)
