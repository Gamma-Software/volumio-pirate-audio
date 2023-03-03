import pygame
from pygame.locals import *

# Create ST7789 LCD Display class.
class ST7789:
    def __init__(self, height, width, rotation, port, cs, dc, backlight, spi_speed_hz, offset_left, offset_top):
        self.screen = pygame.display.set_mode((width, height))
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

        mode = image.mode
        size = image.size
        data = image.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)

        backgroud = py_image.get_rect()
        backgroud.center = self.width//2, self.height//2

        self.screen.fill(0xFFFFFF)
        self.screen.blit(py_image, backgroud)

        # Update the display
        pygame.display.update()