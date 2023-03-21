class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GPIOSingleton(metaclass=SingletonMeta):

    BCM = 0
    IN = 0
    PUD_UP = 0
    FALLING = 0

    def __init__(self) -> None:
        self.buttons = {"5": 0, "6": 0, "16": 0, "20": 0}

    def setmode(self, mode):
        pass

    def cleanup(self, button):
        pass

    def setup(self, channel, pin, direction):
        pass

    def press_key(self, pin):
        if not self.callback or not callable(self.callback):
            return

        self.buttons[str(pin)] = 1
        self.callback(pin)  # Call the callback function only if the button is pressed

    def release_key(self, pin):
        self.buttons[str(pin)] = 0

    def add_event_detect(self, pin_channels, direction, _callback, bouncetime):
        self.callback = _callback

    def input(self, pin):
        ret = self.buttons[str(pin)]
        return not bool(ret)
