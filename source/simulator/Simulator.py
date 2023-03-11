
import sys
import keyboard
from threading import Thread
import source.simulator.GPIO as GPIO

import queue
import json

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
    with open('source/simulator/key_map.json', 'r') as myfile:
        DATA = myfile.read()
        KEYBOARD_MAP = json.loads(DATA)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                for key in KEYBOARD_MAP:
                    if event.key == pygame.key.key_code(KEYBOARD_MAP[key]["map"]):
                        GPIO.press_key(KEYBOARD_MAP[key]["value"])
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.KEYUP:
                for key in KEYBOARD_MAP:
                    if event.key == pygame.key.key_code(KEYBOARD_MAP[key]["map"]):
                        GPIO.release_key(KEYBOARD_MAP[key]["value"])

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