import sys
import typing

from socketIO_client import SocketIO

from source.debug import print_debug, check_perfo
from source.menu.menu import MenuStateMachine
from source.hardware.display import DisplayHandler
from source.hardware.buttons import ButtonHandler
from state_machine import PlayerStateMachine


class Player:
    """
    This is the main class of the player.
    It is responsible for the state machine
    and the socket connection
    and display
    and the buttons
    """

    def __init__(self,
                 display: DisplayHandler, buttons: ButtonHandler,
                 host="localhost", port=3000):
        self.socket = SocketIO(host, port)
        self.menu = None  # None because by default we are in the player
        self.display = display
        self.buttons = buttons
        self.buttons.add_callbacks(self.button_on_click)

        self.player_state_machine = PlayerStateMachine()
        self.player_state_machine.current_state.run()

        self.socket.once('connect', self.socket_on_connect)
        self.socket.on('disconnect', self.socket_on_disconnect)

    def button_on_click(self, button):
        # If the menu is closed, we are in the player
        if not self.menu:  # In Player
            if button == 'b':
                self.sta
            self.menu = MenuStateMachine()  # Start the menu state machine

        # If the menu open
        if self.menu:
            self.state_machine.current_state.button_on_click(button)


    def socket_on_connect(self):
        self.socket.on('pushState', self.socket_on_push_state)
        self.socket.emit('getState', '', self.socket_on_push_state)
        self.socket.on('pushBrowseSources', self.socket_on_push_browsesources)
        self.socket.on('pushBrowseLibrary', self.socket_on_push_browselibrary)
        self.socket.on('pushQueue', self.socket_on_push_queue)
        self.socket.emit('getQueue', self.socket_on_push_queue)

    def socket_on_disconnect(self):
        self.display.display_stuff(IMAGE_DICT['BG_DEFAULT'], OBJ_TRANS['DISPLAY']['LOSTCONNECTION'], 0, 0, 'info')
        pass

    def socket_on_push_state(self, state):
        pass

    @check_perfo
    def socket_on_push_browsesources(
            self, dict_resources: typing.Tuple[typing.List[typing.Dict[str, str]]]):
        """processes websocket informations of browsesources"""
        self.menu.run(dict_resources)

    def socket_on_push_browselibrary(self, data):
        pass

    def socket_on_push_queue(self, queue):
        pass

    def clean(self):
        """cleanes up at exit, even if service is stopped"""
        # display_stuff(IMAGE_DICT['BG_DEFAULT'], OBJ_TRANS['DISPLAY']['SHUTDOWN'], 0, 0, 'info')  # v0.0.7
        # sleep(1)  # v0.0.7
        # DISP.set_backlight(False)
        self.buttons.clean()
        sys.exit(0)
