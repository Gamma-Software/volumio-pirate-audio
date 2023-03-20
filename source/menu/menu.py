import time
import typing

from socketIO_client import SocketIO

from source.hardware.display import DisplayHandler
import source.menu.menu_states as states
from source.utils import MESSAGES_DATA


class MenuStateMachine:

    def __init__(self, socket: SocketIO, update_menu_callback, close_menu_callback):
        self.state = states.MainMenu(MESSAGES_DATA, socket,
                                     self.on_push_browsesources,
                                     self.on_push_browselibrary,
                                     self.on_get_queue)
        self.update_menu_callback = update_menu_callback
        self.close_menu_callback = close_menu_callback
        self.last_states = [states.MenuClosed(states.MainMenu, MESSAGES_DATA, socket,
                                              self.on_push_browsesources,
                                              self.on_push_browselibrary,
                                              self.on_get_queue)]
        self.socket = socket

    def on_push_browsesources(
            self, dict_resources: typing.Tuple[typing.List[typing.Dict[str, typing.Any]]]):
        """processes websocket informations of browsesources"""
        if not isinstance(self.state, states.BrowseSourceMenu):
            return
        self.update_choices(dict_resources)
        self.update_menu_callback()

    def on_push_browselibrary(
            self, dict_resources):
        if not isinstance(self.state, states.BrowseLibraryMenu):
            return
        self.update_choices(dict_resources)
        self.update_menu_callback()

    def on_get_queue(self, dict_queue):
        if not isinstance(self.state, states.PrevNextMenu):
            return
        self.update_choices(dict_queue)
        self.update_menu_callback()

    def on_push_state(self, data):
        if not isinstance(self.state, states.SeekMenu):
            return
        self.state.update_duration(data)
        self.update_menu_callback()

    def open_menu(self):
        self.state = states.MainMenu(MESSAGES_DATA, self.socket,
                                     self.on_push_browsesources,
                                     self.on_push_browselibrary,
                                     self.on_get_queue)
        self.last_states = [states.MenuClosed(states.MainMenu, MESSAGES_DATA, self.socket,
                                              self.on_push_browsesources,
                                              self.on_push_browselibrary,
                                              self.on_get_queue)]
        self.state.run()

    def select(self, cursor):
        self.last_states.append(self.state)
        self.state = self.state.next(cursor)
        if self.state is None:
            print("Error: cannot go to next state")
            return
        self.state.run()
        if isinstance(self.state, states.MenuClosed):
            self.close_menu_callback()

    def update_choices(self, data):
        self.state.update_choices(data)

    def go_back(self):
        if isinstance(self.state, states.MenuClosed):
            print("Error: cannot go back")

        self.state = self.last_states.pop()
        self.state.run()
        if self.last_states == []:
            self.close_menu_callback()


class Menu:
    def __init__(self, socket: SocketIO, display: DisplayHandler) -> None:
        self.socket = socket
        self.state_machine = MenuStateMachine(self.socket, self.update_menu, self.close_menu)
        self.display = display
        self.open = False
        self.cursor = 0

    def register_events(self):
        self.socket.on('pushBrowseSources', self.state_machine.on_push_browsesources)
        self.socket.on('pushBrowseLibrary', self.state_machine.on_push_browselibrary)
        self.socket.on('pushQueue', self.state_machine.on_get_queue)
        self.socket.on('pushState', self.state_machine.on_push_state)

    def cursor_up(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = len(self.state_machine.state.choices) - 1

    def cursor_down(self):
        self.cursor += 1
        if self.cursor >= len(self.state_machine.state.choices):
            self.cursor = 0

    def show_menu(self):
        self.open = True
        self.state_machine.open_menu()
        self.register_events()
        self.update_menu()

    def close_menu(self):
        self.open = False

        if not isinstance(self.state_machine.state, states.MenuClosed):
            return

        if isinstance(self.state_machine.state.close_on, states.SleepTimerMenu):
            self.start_sleep_timer()
        if isinstance(self.state_machine.state.close_on, states.ShutdownMenu):
            self.shutdown()
        if isinstance(self.state_machine.state.close_on, states.RebootMenu):
            self.reboot()

    def shutdown(self):
        self.socket.emit('shutdown')
        self.display.display_shutdown()

    def reboot(self):
        self.socket.emit('reboot')
        self.display.display_reboot()

    def start_sleep_timer(self):
        self.socket.emit('setSleep')  # TODO: add timer

    def update_menu(self):
        if not self.open:
            return

        if hasattr(self.state_machine.state, 'waiting_for_data') and\
           self.state_machine.state.waiting_for_data:
            self.display.display_menu(MESSAGES_DATA['DISPLAY']['WAIT'], 0)
            return

        if isinstance(self.state_machine.state, states.PrevNextMenu):
            self.display.display_menu(self.state_machine.state.choices, self.cursor, 'seek')
            return

        if isinstance(self.state_machine.state, states.SeekMenu):
            if not self.state_machine.state.seek or not self.state_machine.state.current_duration:
                return
            seek_msg = time.strftime("%M:%S", time.gmtime(
                int(float(self.state_machine.state.seek/1000))))
            duration_msg = time.strftime("%M:%S", time.gmtime(
                self.state_machine.state.current_duration))

            self.display.display_menu([MESSAGES_DATA['DISPLAY']['SEEK'],
                                      ''.join([seek_msg, ' / ', duration_msg])], 0, 'seek')
            return

        self.display.display_menu(self.state_machine.state.choices, self.cursor)

    def button_on_click(self, button):
        if not self.open:
            return

        # We can only select if we are not waiting for data
        if hasattr(self.state_machine.state, 'waiting_for_data') and\
           not self.state_machine.state.waiting_for_data:
            if button == 'a':
                self.state_machine.select(self.cursor)
                self.cursor = 0
            if button == 'x':
                self.cursor_up()
                self.state_machine.state.up_down("up")
            if button == 'y':
                self.cursor_down()
                self.state_machine.state.up_down("down")
        if button == 'b':
            self.cursor = 0
            self.state_machine.go_back()

        # Update the menu
        self.update_menu()

        return self.state_machine
