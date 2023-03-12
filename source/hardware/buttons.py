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
            for pin in self.button_mapping:
                GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)
                GPIO.add_event_detect(pin, GPIO.FALLING, self.handle_button, bouncetime=250)
                time.sleep(0.1)  # Wait a bit
        except (ValueError, RuntimeError) as e:
            print('ERROR at setup channel:', e)

    def add_callbacks(self, callback):
        self.callbacks.append(callback)

    def clean(self):
        GPIO.cleanup(list(self.button_mapping.values()))

    def handle_button(self, pin):
        for call in self.callbacks:
            key = list(self.button_mapping.keys())[
                list(self.button_mapping.values()).index(pin)]
            call(key)
