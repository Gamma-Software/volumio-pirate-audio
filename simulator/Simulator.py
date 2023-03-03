import pygame
from pygame.locals import *
from PIL import Image

class Simulator:
    def __init__(self, disp, gpio):
        # Set up Pygame window
        pygame.init()
        self.DISP = disp
        self.gpio = gpio

    def loop(self, image):
        # Display image on LCD
        if image is None:
            image = Image.open('images/default.jpg').resize((240, 240))

        # Display image on LCD simulator
        self.DISP.display(image)

    def handle_events(self):
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Handle keyboard input
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.gpio.press_key("button_a")
                elif event.key == pygame.K_b:
                    self.gpio.press_key("button_b")
                elif event.key == pygame.K_x:
                    self.gpio.press_key("button_x")
                elif event.key == pygame.K_y:
                    self.gpio.press_key("button_y")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.gpio.release_key("button_a")
                elif event.key == pygame.K_b:
                    self.gpio.release_key("button_b")
                elif event.key == pygame.K_x:
                    self.gpio.release_key("button_x")
                elif event.key == pygame.K_y:
                    self.gpio.release_key("button_y")
        return True

    def __del__(self) -> None:
        # Clean up Pygame
        pygame.quit()