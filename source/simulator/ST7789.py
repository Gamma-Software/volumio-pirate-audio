# Create ST7789 LCD Display class.
class ST7789:
    def __init__(self, height, width, rotation, port, cs, dc,
                 backlight, spi_speed_hz, offset_left, offset_top):
        self.height = height
        self.width = width
        self.rotation = rotation
        self.port = port
        self.cs = cs
        self.dc = dc
        self.backlight = backlight
        self.spi_speed_hz = spi_speed_hz
        self.offset_left = offset_left
        self.offset_top = offset_top
        self.image_to_display = None

    def display_callback(self, callback):
        self.callback = callback

    def set_backlight(self, value):
        pass

    def display(self, image):
        if self.callback and callable(self.callback):
            self.callback(image)
