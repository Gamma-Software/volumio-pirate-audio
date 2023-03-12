import sys
import time
import typing
import requests
from io import BytesIO

from source.debug import print_debug, check_perfo
from source.menu.menu import Menu
from source.hardware.display import DisplayHandler
from source.hardware.buttons import ButtonHandler
from .state_machine import PlayerStateMachine

from source import SIMULATOR

if SIMULATOR:
    from source.simulator.Simulator import Simulator
    simulator = Simulator()


class Player:
    """
    This is the main class of the player.
    It is responsible for the state machine
    and the socket connection
    and display
    and the buttons
    """

    def __init__(self,
                 socket,
                 display: DisplayHandler, buttons: ButtonHandler, menu: Menu,
                 host="localhost", port=3000):
        self.socket = socket
        self.remote_host = host
        self.remote_port = port
        self.menu = menu
        self.menu.add_listener(self.on_menu_close, "close")
        self.menu.add_listener(self.reboot, "reboot")
        self.menu.add_listener(self.shutdown, "shutdown")
        self.display = display
        if SIMULATOR:
            self.display.display.display_callback(simulator.display_image)
        self.buttons = buttons
        self.buttons.add_callbacks(self.button_on_click)
        self.last_data = None

        self.player_state_machine = PlayerStateMachine()

    def refresh(self):
        """helper function as thread"""
        self.socket.emit('getState', '', self.socket_on_push_state)
        return

    def start(self):
        print("Starting player main loop")

        self.display.display_connect()
        if SIMULATOR:
            print("... and the simulator")
            simulator.start(self.socket)

    def button_on_click(self, button):
        print("Button pressed: " + str(button))
        # If the menu is closed, we are in the player
        if not self.menu.open:  # In Player
            if button == 'b':
                self.player_state_machine.volume_down()
                self.socket.emit('volume', '-')
                time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                self.last_data["volume"] = self.player_state_machine.current_volume
                self.socket_on_push_state(self.last_data)

            if button == 'y':
                self.player_state_machine.volume_up()
                self.socket.emit('volume', '+')
                time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                self.last_data["volume"] = self.player_state_machine.current_volume
                self.socket_on_push_state(self.last_data)

            if button == 'x':
                self.menu.show_menu()
                self.buttons.add_callbacks(self.menu.button_on_click, priority=1)

            if button == 'a':
                new_state = self.player_state_machine.play_pause()
                self.socket.emit(new_state)
                time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                self.last_data["status"] = new_state
                self.socket_on_push_state(self.last_data)

    def on_menu_close(self):
        self.buttons.remove_callbacks(self.menu.button_on_click)
        self.socket_on_push_state(self.last_data)

    def shutdown(self):
        self.socket.emit('shutdown')
        self.display.display_shutdown()

        self.buttons.remove_all_listeners()
        self.menu.remove_all_listeners()

    def reboot(self):
        self.socket.emit('reboot')
        self.display.display_reboot()

        self.buttons.remove_all_listeners()
        self.menu.remove_all_listeners()

    def start_sleep_timer(self):
        self.socket.emit('setSleep')  # TODO: add timer

    def socket_on_connect(self):
        self.socket.on('pushState', self.socket_on_push_state)
        self.socket.emit('getState', '', self.socket_on_push_state)
        self.socket.on('pushBrowseSources', self.socket_on_push_browsesources)
        self.socket.on('pushBrowseLibrary', self.socket_on_push_browselibrary)
        self.socket.on('pushQueue', self.socket_on_push_queue)
        self.socket.emit('getQueue', self.socket_on_push_queue)

    def socket_on_disconnect(self):
        self.display.display_disconnect()

    @check_perfo
    def socket_on_push_state(self,
                             data: typing.Tuple[typing.Dict[str, typing.Any]]):
        print_debug(f"State received {data}")
        self.last_data = data

        if not data['title'] and not data['artist'] \
           and not data['album'] and len(self.player_state_machine.queue) > 0:
            return

        state = ''.join([data['status'],
                         data['title'],
                         str(data['volume']),
                         str(data['seek'])])
        if self.player_state_machine.last_state != state and not self.menu.open:
            self.player_state_machine.parse_data(data)

            # May take a while TODO refactor
            if "http" not in data['albumart']:
                albumart_url = ''.join([f'http://{self.remote_host}:{self.remote_port}',
                                        data['albumart'].encode('ascii', 'ignore').decode('utf-8')])
            else:  # in case the albumart is already local file
                albumart_url = data['albumart'].encode('ascii', 'ignore').decode('utf-8')

            # Download album art only if it changed
            if self.player_state_machine.music_data.album_uri != albumart_url:
                self.last_response = requests.get(albumart_url)
                self.player_state_machine.music_data.album_uri = albumart_url

            self.player_state_machine.music_data.album_art = self.display.f_background(
                BytesIO(self.last_response.content))

            self.display.f_displayoverlay(self.player_state_machine.status,
                                          self.player_state_machine.current_volume,
                                          data)
            self.display.f_timebar(data, self.player_state_machine.duration)

            # display only if img changed
            #if self.display.screen.image_check != self.display.screen.current_image:
            self.display.screen.image_check = self.display.screen.current_image
            self.display.sendtodisplay(self.display.screen.current_image)

    def socket_on_push_browsesources(
            self, dict_resources: typing.Tuple[typing.List[typing.Dict[str, typing.Any]]]):
        """processes websocket informations of browsesources"""
        self.menu.run(dict_resources)

    def socket_on_push_browselibrary(self, data):
        pass

    def socket_on_push_queue(self, queue):
        self.player_state_machine.queue = queue

    def clean(self):
        """cleanes up at exit, even if service is stopped"""
        self.display.clean()
        self.buttons.remove_all_listeners()
        self.menu.remove_all_listeners()
        sys.exit(0)
