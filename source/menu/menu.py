import typing

from socketIO_client import SocketIO

from source.hardware.display import DisplayHandler
import source.menu.menu_states as states
from source.utils import MESSAGES_DATA


class MenuStateMachine:

    def __init__(self, callback=None):
        self.state = states.main_menu_state
        self.last_state = None
        self.callback = callback

    def open_menu(self):
        self.state = states.main_menu_state
        self.last_state = None
        self.state.run(self.callback)

    def select(self, cursor):
        self.last_state = self.state
        self.state = self.state.next(cursor)
        if self.state is None:
            print("Error: cannot go to next state")
            return
        self.state.run(self.callback)

    def go_back(self) -> bool:
        if self.state == states.close_menu_state:
            print("Error: cannot go back")
            return

        self.state = self.state.previous()
        if self.state is None:
            print("Error: cannot go to next state")
            return
        self.state.run(self.callback)


class Menu:
    def __init__(self, socket: SocketIO, display: DisplayHandler) -> None:
        self.socket = socket
        self.state_machine = MenuStateMachine(self.on_menu_actions)
        self.display = display
        self.open = False
        self.cursor = 0

    def socket_on_connect(self):
        self.socket.on('pushBrowseSources', self.socket_on_push_browsesources)
        self.socket.on('pushBrowseLibrary', self.socket_on_push_browselibrary)

    def socket_on_push_browsesources(
            self, dict_resources: typing.Tuple[typing.List[typing.Dict[str, typing.Any]]]):
        """processes websocket informations of browsesources"""
        if self.state_machine.state != states.browse_source_menu_state:
            return
        self.state_machine.state.update_choices(dict_resources)
        self.state_machine.state.run(dict_resources)
        self.update_menu()

    def socket_on_push_browselibrary(
            self, dict_resources):
        if self.state_machine.state != states.browse_library_menu_state:
            return
        self.state_machine.state.update_choices(dict_resources)
        self.state_machine.state.run()
        self.update_menu()

    def cursor_up(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = len(self.state_machine.state.choices) - 1

    def cursor_down(self):
        self.cursor += 1
        if self.cursor >= len(self.state_machine.state.choices):
            self.cursor = 0

    def on_menu_actions(self):
        if self.state_machine.state == states.browse_library_menu_state:
            self.socket.emit('browseLibrary', {'uri': self.state_machine.state.choices[self.cursor]['uri']})
        if self.state_machine.state == states.browse_source_menu_state:
            self.socket.emit('getBrowseSources', '', self.socket_on_push_browsesources)

    def show_menu(self):
        self.open = True
        self.state_machine.open_menu()
        self.update_menu()

    def close_menu(self):
        self.open = False

    def update_menu(self):
        if self.open:
            if self.state_machine.state.waiting_for_data:
                self.display.display_menu(MESSAGES_DATA['DISPLAY']['WAIT'], 0)
            else:
                self.display.display_menu(self.state_machine.state.choices, self.cursor)

    def button_on_click(self, button):
        if not self.open:
            return

        if button == 'a':
            self.cursor = 0
            self.state_machine.select(self.cursor)
        if button == 'x':
            self.cursor_up()
        if button == 'y':
            self.cursor_down()
        if button == 'b':
            self.cursor = 0
            self.state_machine.go_back()
            if self.state_machine.state == states.close_menu_state:
                self.close_menu()

        # Update the menu
        self.update_menu()

        return self.state_machine
