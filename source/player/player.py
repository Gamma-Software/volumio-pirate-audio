import sys
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
        self.display = display
        if SIMULATOR:
            self.display.display.display_callback(simulator.display_image)
        self.buttons = buttons
        self.buttons.add_callbacks(self.button_on_click)
        self.buttons.add_callbacks(self.menu.button_on_click)
        self.last_data = None

        self.player_state_machine = PlayerStateMachine()

    def refresh(self):
        """helper function as thread"""
        self.socket.emit('getState', '', self.socket_on_push_state)
        return

        """#if WS_CONNECTED and VOLUMIO_DICT['SERVICE'] not in ['webradio'] and VOLUMIO_DICT['STATUS'] not in ['stop', 'pause'] and VOLUMIO_DICT['MODE'] == 'player' and time() >= IMAGE_DICT['LASTREFRESH'] + 4.5: # v0.0.7 hint pylint
        if self.player_state_machine.last_state and VOLUMIO_DICT['SERVICE'] not in ['webradio'] and VOLUMIO_DICT['STATUS'] not in ['stop', 'pause'] and VOLUMIO_DICT['MODE'] == 'player' and time() >= IMAGE_DICT['LASTREFRESH'] + 4.5: # v0.0.7 hint pylint
            SOCKETIO.emit('getState')

        global screen_in_sleep, last_time_button_pushed

        if time() >= last_time_button_pushed + wait_sleep_screen and not screen_in_sleep:
            if VOLUMIO_DICT['MODE'] == 'player':
                screen_in_sleep = True
                DISP.set_backlight(False)
            else:
                reset_variable('player') # Go back to player mode if no button is pushed for 10 seconds
                IMAGE_DICT['LASTREFRESH'] = time()-5  # to get display refresh independ from refresh thread
                SOCKETIO.emit('getState')
                last_time_button_pushed = time()"""

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
                # No need to wait for the getState, it will be updated by the pushState
                self.last_data["volume"] = self.player_state_machine.current_volume
                self.socket_on_push_state(self.last_data)
            if button == 'y':
                self.player_state_machine.volume_up()
                self.socket.emit('volume', '+')
                # No need to wait for the getState, it will be updated by the pushState
                self.last_data["volume"] = self.player_state_machine.current_volume
                self.socket_on_push_state(self.last_data)
            if button == 'x':
                #self.menu.show_menu()
                print("Menu not implemented yet")
                pass
            if button == 'a':
                new_state = self.player_state_machine.play_pause()
                self.socket.emit(new_state)
                # No need to wait for the getState, it will be updated by the pushState
                self.last_data["status"] = new_state
                self.socket_on_push_state(self.last_data)

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
            else:
                albumart_url = data['albumart'].encode('ascii', 'ignore').decode('utf-8')

            if self.player_state_machine.music_data.album_uri != albumart_url:
                response = requests.get(albumart_url)
                self.player_state_machine.music_data.album_uri = albumart_url
                self.player_state_machine.music_data.album_art = self.display.f_background(
                    BytesIO(response.content))

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
        self.buttons.clean()
        sys.exit(0)
