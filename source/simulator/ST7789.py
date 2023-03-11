from source.simulator.Simulator import image_queue


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

    def set_backlight(self, value):
        print("backlight Not implemented on simulator")

    def display(self, image):
        # put the image in the queue
        image_queue.put(image)
