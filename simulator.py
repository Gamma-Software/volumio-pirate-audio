import pygame
from pygame.locals import *
from PIL import Image

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

def main():
    # Set up Pygame window
    pygame.init()
    window = pygame.display.set_mode((240, 240))

    # Create ST7789 LCD Display object
    DISP = ST7789(
        height=240,
        width=240,
        rotation=90,
        port=0,
        cs=1,
        dc=9,
        backlight=13,
        spi_speed_hz=80 * 1000 * 1000,
        offset_left=0,
        offset_top=0
    )

    # Main loop
    running = True
    while running:
        # Generate random image
        #image = [[(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(240)] for _ in range(240)]

        # Display image on LCD
        image = Image.open('images/default.jpg').resize((240, 240))

        # Display image on LCD simulator
        DISP.display(image)

        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # Clean up Pygame
    pygame.quit()


if __name__ == '__main__':
    main()