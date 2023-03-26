import json
import time
from PIL import Image

from source import SIMULATOR
if SIMULATOR:
    import pygame
    from source.simulator.gpio import GPIOSingleton  # simulator
    GPIO = GPIOSingleton()


class Simulator:
    def __init__(self):
        if not SIMULATOR:
            raise RuntimeError("Simulator is not enabled")
        pygame.init()
        pygame.display.set_caption("PirateAudio-Volumio Simulator")
        self.screen = pygame.display.set_mode((240, 240))
        self.image_to_display = None

    def start(self, socket):
        # Main game loop
        self.socket = socket
        self.loop()

    def loop(self):
        running = True
        show_fps = False
        with open('source/simulator/key_map.json', 'r') as myfile:
            DATA = myfile.read()
            KEYBOARD_MAP = json.loads(DATA)

        while running:
            start = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    for key in KEYBOARD_MAP:
                        if event.key == pygame.key.key_code(KEYBOARD_MAP[key]["map"]):
                            GPIO.press_key(KEYBOARD_MAP[key]["value"])
                    if event.key == pygame.key.key_code("f"):
                        show_fps = not show_fps
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.KEYUP:
                    for key in KEYBOARD_MAP:
                        if event.key == pygame.key.key_code(KEYBOARD_MAP[key]["map"]):
                            GPIO.release_key(KEYBOARD_MAP[key]["value"])

            if self.image_to_display is not None:
                backgroud = self.image_to_display.get_rect()
                backgroud.center = (self.image_to_display.get_width()//2,
                                    self.image_to_display.get_height()//2)

                if self.screen is None:
                    continue

                self.screen.fill(0xFFFFFF)
                self.screen.blit(self.image_to_display, backgroud)

                pygame.display.flip()
                self.image_to_display = None  # reset to avoid flickering
            time.sleep(0.01)

            if show_fps:
                print("FPS: ", 1/(time.time() - start))

        # Done! Time to quit.
        pygame.quit()

    def display_image(self, image: Image):
        self.image_to_display = self.convert_pillow_image(image)

    def convert_pillow_image(self, pilImage):
        return pygame.image.fromstring(
            pilImage.tobytes(), pilImage.size, pilImage.mode).convert()
