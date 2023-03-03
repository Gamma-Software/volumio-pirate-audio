
import sys
import keyboard
from threading import Thread
import simulator.GPIO as GPIO

import queue

# create a queue to share image between threads
image_queue = queue.Queue()

def simulate(background_task):
    import pygame
    pygame.init()
    pygame.display.set_caption("PirateAudio-Volumio Simulator")
    screen = pygame.display.set_mode((240, 240))

    # Start the background task in a new process
    THREAD = Thread(target=background_task)  # v0.0.7
    THREAD.daemon = True  # v0.0.7
    THREAD.start()  # v0.0.7

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    GPIO.press_key(5)
                elif event.key == pygame.K_b:
                    GPIO.press_key(6)
                elif event.key == pygame.K_x:
                    GPIO.press_key(16)
                elif event.key == pygame.K_y:
                    GPIO.press_key(20)
                elif event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    GPIO.release_key(5)
                elif event.key == pygame.K_b:
                    GPIO.release_key(6)
                elif event.key == pygame.K_x:
                    GPIO.release_key(16)
                elif event.key == pygame.K_y:
                    GPIO.release_key(20)

        try:
            img = image_queue.get(block=False, timeout=0.1)
        except queue.Empty:
            continue
        mode = img.mode
        size = img.size
        data = img.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)

        backgroud = py_image.get_rect()
        backgroud.center = py_image.get_width()//2, py_image.get_height()//2

        screen.fill(0xFFFFFF)
        screen.blit(py_image, backgroud)

        pygame.display.update()
        image_queue.task_done()
    pygame.quit()


def handle_events():
    # Handle Pygame events

    keyboard.on_press_key("a", lambda _: print("You pressed A!"))

    return 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # Handle keyboard input
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.gpio.press_key("5")
            elif event.key == pygame.K_b:
                self.gpio.press_key("6")
            elif event.key == pygame.K_x:
                self.gpio.press_key("16")
            elif event.key == pygame.K_y:
                self.gpio.press_key("20")
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.gpio.release_key("5")
            elif event.key == pygame.K_b:
                self.gpio.release_key("6")
            elif event.key == pygame.K_x:
                self.gpio.release_key("16")
            elif event.key == pygame.K_y:
                self.gpio.release_key("20")
            elif event.key == pygame.K_ESCAPE:
                # Clean up Pygame
                pygame.quit()
                sys.exit(0)
