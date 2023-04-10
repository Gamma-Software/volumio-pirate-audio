from socketIO_client import SocketIO

from source.hardware.display import DisplayHandler
import source.menu.menu_states as states
from source.utils import MESSAGES_DATA


class Menu:
    def __init__(self, socket: SocketIO, display: DisplayHandler) -> None:
        self.socket = socket
        self.display = display
        self.open = False
        self.current_state = states.MainMenu(MESSAGES_DATA, socket, display)
        self.last_states = [states.MenuClosed(states.MainMenu, MESSAGES_DATA, socket, display)]

    def show_menu(self):
        self.open = True
        self.current_state = states.MainMenu(MESSAGES_DATA, self.socket, self.display)
        self.last_states = [states.MenuClosed(states.MainMenu, MESSAGES_DATA,
                                              self.socket, self.display)]
        self.current_state.run()

    def close_menu(self):
        self.open = False

        if not isinstance(self.current_state, states.MenuClosed):
            return

        # Post closing actions
        if self.current_state.close_on == "SleepTimerMenu":
            self.start_sleep_timer()
        if self.current_state.close_on == "ShutdownMenu":
            # Freeze the display on shutdown screen
            self.display.display_menu(self.messages["DISPLAY"]['SHUTINDOWN'], 0, 0, 'info')
        if self.current_state.close_on == "RebootMenu":
            # Freeze the display on reboot screen
            self.display.display_menu(self.messages["DISPLAY"]['REBOOTING'], 0, 0, 'info')

    def start_sleep_timer(self):
        self.socket.emit('setSleep')  # TODO: add timer

    def button_on_click(self, button):
        if not self.open:
            return

        if button == 'a':
            self.last_states.append(self.current_state)
            self.current_state.select()
            self.current_state = self.current_state.next()
            if self.current_state is None:
                print("Error: cannot go to next state")
                self.current_state = self.last_states.pop()
                return
            self.current_state.run()
            if isinstance(self.current_state, states.MenuClosed):
                self.close_menu()
        if button == 'x':
            self.current_state.up_down("up")
        if button == 'y':
            self.current_state.up_down("down")
        if button == 'b':
            self.cursor = 0

            if isinstance(self.current_state, states.MenuClosed):
                print("Error: cannot go back")

            self.current_state = self.last_states.pop()
            self.current_state.run()
            if self.last_states == []:
                self.close_menu()
