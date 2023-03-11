#!/usr/bin/env python3

from pathlib import Path

from source import SIMULATOR

from source.player.state_machine import PlayerStateMachine
from source.player.player import Player
from source.hardware.display import DisplayHandler
from source.hardware.buttons import ButtonHandler
from source.menu.menu import Menu

import os
import os.path
import signal
import json
from PIL import ImageFont


if SIMULATOR:
    import simulator.Simulator as Simulator

SCRIPT_DATA_PATH = Path(__file__).parent.absolute()


if SIMULATOR:
    remote_server = 'volumio.local'
    remote_port = 3000
else:
    remote_server = 'localhost'
    remote_port = 3000


def read_config(config_file) -> dict:
    with open(config_file, 'r') as filestream:
        data = filestream.read()
    return json.loads(data)


def init():
    config_root_path = "/data/configuration/" if not SIMULATOR else ""
    plugin_root_path = "/data/plugins/system_hardware/" if not SIMULATOR else ""

    # read json file (plugin values)
    config_file = config_root_path + ('system_hardware/pirateaudio/config.json' if not SIMULATOR else 'config.json')
    config_data = read_config(config_file)

    # read json file (volumio language)
    lang_file = config_root_path + ('miscellanea/appearance/config.json' if not SIMULATOR else 'misc_config.json')
    language_code = read_config(lang_file)['language_code']['value']

    messages_data_path = ''.join([(plugin_root_path + 'pirateaudio/' if not SIMULATOR else '') + 'i18n/strings_', language_code, '.json'])  # v0.0.7
    if not os.path.exists(messages_data_path):  # fallback to en as default language
        messages_data_path = (plugin_root_path + 'pirateaudio/' if not SIMULATOR else '') + 'i18n/strings_en.json'

    # read json file (language file for translation)
    messages_data = read_config(messages_data_path)

    fonts = {
        "FONT_S": ImageFont.truetype(
            os.path.join(SCRIPT_DATA_PATH, 'fonts/Roboto-Medium.ttf'), 20),
        "FONT_M": ImageFont.truetype(
            os.path.join(SCRIPT_DATA_PATH, '/fonts/Roboto-Medium.ttf'), 24),
        "FONT_L": ImageFont.truetype(
            os.path.join(SCRIPT_DATA_PATH, '/fonts/Roboto-Medium.ttf'), 30),
        "FONT_FAS": ImageFont.truetype(
            os.path.join(SCRIPT_DATA_PATH, '/fonts/FontAwesome5-Free-Solid.otf'), 28)
    }

    if SIMULATOR:
        remote_server = 'volumio.local'
        remote_port = 3000
    else:
        remote_server = 'localhost'
        remote_port = 3000

    display = DisplayHandler(fonts, messages_data)
    buttons = ButtonHandler({"a": 5, "b": 6, "x": 16, "y": 20})  # TODO make this configurable
    menu = Menu()
    player = Player(display, buttons, menu, remote_server, remote_port)

    for sig in (signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
        signal.signal(sig, player.clean)
    return player


if __name__ == "__main__":
    player = init()
    player.start()
