import multiprocessing
import time
import pygame

def background_task():
    while True:
        print('Background task running...')
        time.sleep(1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('My Game')

    # Start the background task in a new process
    process = multiprocessing.Process(target=background_task)
    process.start()

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        pygame.display.update()

    # Clean up and terminate the background process
    process.terminate()
    process.join()
    pygame.quit()

if __name__ == '__main__':
    main()