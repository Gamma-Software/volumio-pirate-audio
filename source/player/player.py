import sys
import time
import typing
import requests
from copy import deepcopy
from io import BytesIO

from source.debug import print_debug, check_perfo
from source.menu.menu import Menu
from source.hardware.display import DisplayHandler
from source.hardware.buttons import ButtonHandler
from .state_machine import PlayerStateMachine, STATE_PLAY

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
        self.display = display
        if SIMULATOR:
            self.display.display.display_callback(simulator.display_image)
        self.buttons = buttons
        self.buttons.add_callbacks(self.button_on_click)
        self.last_data = None
        self.player_state_machine = PlayerStateMachine()

        self.socket.once('connect', self.register_events)
        self.socket.on('disconnect', self.socket_on_disconnect)

    def refresh(self):
        """helper function as thread"""
        self.socket.emit('getState', '', self.socket_on_push_state)

    def start(self):
        print("Starting player main loop")

        self.display.display_connect()
        try:
            if SIMULATOR:
                print("... and the simulator")
                simulator.start(self.socket)
            else:
                while True:
                    if self.player_state_machine.status == STATE_PLAY:
                        current_time = time.time()
                        self.refresh()
                        # Wait for the next refresh to be at least 1 second after the last one
                        time.sleep(max(0, 1 - (time.time() - current_time)))
                    else:
                        time.sleep(5)
        except KeyboardInterrupt:
            self.clean()

    def button_on_click(self, button):
        #print("Button pressed: " + str(button))
        # If the menu is closed, we are in the player
        if not self.menu.open:  # In Player
            if button == 'b':
                self.player_state_machine.volume_down()
                self.socket.emit('volume', '-')
                time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                data_to_send = deepcopy(self.last_data)
                data_to_send["volume"] = self.player_state_machine.current_volume
                self.socket_on_push_state(data_to_send)

            if button == 'y':
                self.player_state_machine.volume_up()
                self.socket.emit('volume', '+')
                time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                data_to_send = deepcopy(self.last_data)
                data_to_send["volume"] = self.player_state_machine.current_volume
                self.socket_on_push_state(data_to_send)

            if button == 'x':
                self.menu.show_menu()

            if button == 'a':
                new_state = self.player_state_machine.play_pause()
                self.socket.emit(new_state)
                time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                data_to_send = deepcopy(self.last_data)
                data_to_send["status"] = new_state
                self.socket_on_push_state(data_to_send)

        # If the menu is open, we are in the menu
        else:
            self.menu.button_on_click(button)

            # After the button is pressed, we check if the menu is still open
            if not self.menu.open:
                if self.menu.current_state.close_on == None:
                    return
                self.socket_on_push_state(self.last_data, True)
                self.register_events()  # Get back the callbacks
                self.socket.emit('getState', '', self.socket_on_push_state)

    def register_events(self):
        self.socket.on('pushState', self.socket_on_push_state)
        self.socket.emit('getState', '', self.socket_on_push_state)

    def socket_on_disconnect(self):
        self.display.display_disconnect()

    @check_perfo
    def socket_on_push_state(self,
                             data: typing.Tuple[typing.Dict[str, typing.Any]],
                             force=False):
        if data == self.last_data and not force:
            return

        self.last_data = data

        if 'album' in data.keys():
            if not data['album']:
                data['album'] = ""  # In case of radio, album is not set

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
            # TODO integrate this in the state machine
            if self.player_state_machine.last_music_data.album_art != \
               self.player_state_machine.music_data.album_art:
                self.player_state_machine.music_data.album_url = albumart_url
                self.display.f_background(BytesIO(requests.get(albumart_url).content))

            self.display.f_displayoverlay(self.player_state_machine.status,
                                          self.player_state_machine.current_volume,
                                          data)
            if self.player_state_machine.music_data.duration:
                self.display.f_timebar(data, self.player_state_machine.music_data.duration)

            # display only if img changed
            #if self.display.screen.image_check != self.display.screen.current_image:
            self.display.screen.image_check = self.display.screen.current_image
            self.display.sendtodisplay(self.display.screen.current_image)

            # TODO integrate this in the state machine
            self.player_state_machine.last_music_data = deepcopy(
                self.player_state_machine.music_data)

    def socket_on_push_queue(self, queue):
        self.player_state_machine.queue = queue

    def clean(self):
        """cleanes up at exit, even if service is stopped"""
        self.display.clean()
        self.buttons.remove_all_listeners()
        self.menu.remove_all_listeners()
        sys.exit(0)
