from source import SIMULATOR

if SIMULATOR:
    import simulator.GPIO as GPIO  # simulator
else:
    import RPi.GPIO as GPIO


class ButtonHandler:
    def __init__(self, button_mapping) -> None:
        self.button_mapping = button_mapping
        self.callbacks = None
        GPIO.setmode(GPIO.BCM)

    def add_callbacks(self, callback):
        self.callbacks.append(callback)

    def clean(self):
        GPIO.cleanup(list(self.button_mapping.values()))

    def handle_button(self, pin):
        for call in self.callbacks:
            call(self.button_mapping[pin])
