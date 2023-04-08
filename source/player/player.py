import sys
import time
import typing
import threading
from copy import deepcopy

from source.debug import check_perfo, print_debug
from source.menu.menu import Menu
from source.hardware.display import DisplayHandler
from source.hardware.buttons import ButtonHandler
from .state_machine import PlayerStateMachine, STATE_PLAY

from source import SIMULATOR

if SIMULATOR:
    from source.simulator.Simulator import Simulator
    simulator = Simulator()


class ScreenSleepData:
    def __init__(self, time_to_sleep) -> None:
        self.sleeping = False
        self.time_to_sleep = time_to_sleep
        self.timer = time()


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
        self.refresh()

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
                    time.sleep(1)
                    continue
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
        # If the menu is closed, we are in the player
        if not self.menu.open:  # In Player
            if button == 'b':
                self.player_state_machine.volume_down()
                self.socket.emit('volume', '-')
                # time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                # data_to_send = deepcopy(self.last_data)
                # data_to_send["volume"] = self.player_state_machine.current_volume
                # self.socket_on_push_state(data_to_send)

            if button == 'y':
                self.player_state_machine.volume_up()
                self.socket.emit('volume', '+')
                # time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                # data_to_send = deepcopy(self.last_data)
                # data_to_send["volume"] = self.player_state_machine.current_volume
                # self.socket_on_push_state(data_to_send)

            if button == 'x':
                self.menu.show_menu()

            if button == 'a':
                new_state = self.player_state_machine.play_pause()
                self.socket.emit(new_state)
                # time.sleep(0.1)
                # No need to wait for the getState, it will be updated by the pushState
                # data_to_send = deepcopy(self.last_data)
                # data_to_send["status"] = new_state
                # self.socket_on_push_state(data_to_send)

        # If the menu is open, we are in the menu
        else:
            self.menu.button_on_click(button)

            # After the button is pressed, we check if the menu is still open
            if not self.menu.open:
                if self.menu.current_state.close_on is None:
                    return
                # self.socket_on_push_state(self.last_data, True)
                self.register_events()  # Get back the callbacks
                self.socket.emit('getState', '', self.socket_on_push_state)

    def register_events(self):
        self.socket.on('pushState', self.socket_on_push_state)

    def socket_on_disconnect(self):
        self.display.display_disconnect()

    def refresh_display_after_download(self):
        # Limit the quick refresh to 1 per second
        time_to_wait = max(0, 1 - (time.time() - self.display.last_refresh))
        time.sleep(time_to_wait)
        self.display.display_player(self.player_state_machine.music_data,
                                    self.player_state_machine.current_volume,
                                    self.player_state_machine.status,
                                    self.player_state_machine.current_position,
                                    redraw_static=True)

    def clean_data(self, data):
        """ Clean the data received from the socket
        Volumio sends some weird data sometimes
        """
        if not data:
            return
        # Uniformize the data
        for key in ["status", "position", "title", "artist", "album", "albumart", "seek", "uri",
                    "trackType", "seek", "duration", "random", "repeat", "repeatSingle", "consume",
                    "volume", "dbVolume", "mute", "disableVolumeControl", "stream", "updatedb",
                    "volatile", "service"]:
            if key not in data.keys() or data[key] == "":
                data[key] = None

        # Do not take the seek data into account when the radio is playing -> set it to 0
        if data['service'] == "webradio" and data['seek'] != 0:
            data['seek'] = 0
        if 'artist' not in data or (data['service'] == "webradio" and data['artist'] != None):
            data['artist'] = None
        if 'artist' in data and data['artist'] == "":
            data['artist'] = None
        if 'title' in data and data['title'] == "":
            data['title'] = None
        if 'album' in data and data['album'] == "":
            data['album'] = None
        # Remove bitrate, not used
        if 'bitrate' in data:
            del data['bitrate']

        return data

    @staticmethod
    def compare_data(data_a, data_b):
        if data_a is None or data_b is None:
            return False
        for key in ["status", "position", "title", "artist", "album", "albumart", "seek", "uri",
                    "trackType", "seek", "duration", "random", "repeat", "repeatSingle", "consume",
                    "volume", "dbVolume", "mute", "disableVolumeControl", "stream", "updatedb",
                    "volatile", "service"]:
            if key not in data_a.keys():
                print_debug("Key {} not in data_a".format(key))
                return False
            if key not in data_b.keys():
                print_debug("Key {} not in data_b".format(key))
                return False
            if data_a[key] != data_b[key]:
                print_debug("Key {} is different".format(key))
                return False
        return True

    def socket_on_push_state(self,
                             data: typing.Tuple[typing.Dict[str, typing.Any]],
                             force=False):
        data = self.clean_data(data)
        self.last_data = self.clean_data(self.last_data)

        if self.compare_data(data, self.last_data) and not force:
            return
        #print("Received data: {}".format(data))
        self.last_data = data

        if data['service'] == "mdp":
            return

        if 'album' in data.keys():
            if not data['album']:
                data['album'] = ""  # In case of radio, album is not set

        if 'title' in data.keys() and 'artist' in data.keys()\
            and not data['title'] and not data['artist']\
                and not data['album'] and len(self.player_state_machine.queue) > 0:
            return

        state = ''.join([data['status'],
                         data['title'],
                         str(data['volume']),
                         str(data['seek'])])

        if self.player_state_machine.last_state != state and not self.menu.open:
            self.player_state_machine.parse_player_data(data)

        if not self.menu.open:
            self.player_state_machine.parse_music_data(data, self.remote_host, self.remote_port,
                                                       self.refresh_display_after_download)

        if self.player_state_machine.music_changed:
            self.display.display_player(self.player_state_machine.music_data,
                                        self.player_state_machine.current_volume,
                                        self.player_state_machine.status,
                                        self.player_state_machine.current_position,
                                        redraw_static=True)
            self.player_state_machine.music_changed = False
        else:
            self.display.display_player(self.player_state_machine.music_data,
                                        self.player_state_machine.current_volume,
                                        self.player_state_machine.status,
                                        self.player_state_machine.current_position)

    def socket_on_push_queue(self, queue):
        self.player_state_machine.queue = queue

    def clean(self):
        """cleanes up at exit, even if service is stopped"""
        self.display.clean()
        self.buttons.remove_all_listeners()
        self.menu.remove_all_listeners()
        sys.exit(0)
