#!/usr/bin/env python3

import os
import os.path
import signal
from threading import Thread
from PIL import ImageFont
from pathlib import Path
from socketIO_client import SocketIO
from source import SIMULATOR
from source.player.player import Player
from source.hardware.display import DisplayHandler
from source.hardware.buttons import ButtonHandler
from source.menu.menu import Menu
from source.debug import check_perfo
from source.utils import MESSAGES_DATA, CONFIG_DATA

SCRIPT_ROOT_PATH = Path(__file__).parent.parent.absolute()


@check_perfo
def init():
    fonts = {
        "FONT_S": ImageFont.truetype(
            os.path.join(SCRIPT_ROOT_PATH, 'fonts/Roboto-Medium.ttf'), 20),
        "FONT_M": ImageFont.truetype(
            os.path.join(SCRIPT_ROOT_PATH, 'fonts/Roboto-Medium.ttf'), 24),
        "FONT_L": ImageFont.truetype(
            os.path.join(SCRIPT_ROOT_PATH, 'fonts/Roboto-Medium.ttf'), 30),
        "FONT_FAS": ImageFont.truetype(
            os.path.join(SCRIPT_ROOT_PATH, 'fonts/FontAwesome5-Free-Solid.otf'), 28)
    }

    display = DisplayHandler(fonts, MESSAGES_DATA)
    # TODO make this configurable
    buttons = ButtonHandler({"a": 5, "b": 6, "x": 16, "y": CONFIG_DATA['gpio_ybutton']['value']})
    remote_host = 'localhost' if not SIMULATOR else 'volumio.local'
    socket = SocketIO(remote_host, 3000)
    menu = Menu(socket, display)
    player = Player(socket, display, buttons, menu, remote_host, 3000)

    def socket_thread():
        print("Socket thread started")
        socket.wait()

    thread = Thread(target=socket_thread)
    thread.daemon = True

    for sig in (signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
        signal.signal(sig, player.clean)
    return player, thread


def main():
    player, socket_thread = init()

    # Start threads
    socket_thread.start()
    player.start()


if __name__ == "__main__":
    main()
