from source.hardware.display import DisplayHandler
import source.menu.menu_states as states


class MenuStateMachine:

    def __init__(self):
        self.current_menu = states.main_menu_state

    def open_menu(self):
        self.current_menu = states.main_menu_state
        self.current_menu.run()

    def select(self, cursor):
        self.current_menu = self.current_menu.next(cursor)
        if self.current_menu is None:
            raise Exception("Error: cannot go to next state")
        self.current_menu.run()

    def go_back(self) -> bool:
        if self.current_menu == states.close_menu_state:
            print("Error: cannot go back")
            return

        self.current_menu = self.current_menu.previous()
        self.current_menu.run()


class Menu:
    def __init__(self, display: DisplayHandler) -> None:
        self.state = MenuStateMachine()
        self.display = display
        self.open = False
        self.cursor = 0
        self.listeners = []

    def clean(self):
        self.remove_all_listeners()

    def remove_all_listeners(self):
        self.listeners = []

    def add_listener(self, listener, name, priority=0):
        if listener in self.listeners:
            return
        if priority == 0:
            self.listeners.insert(0, (name, listener))
        else:
            self.listeners.append((name, listener))

    def cursor_up(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = len(self.state.current_menu.choices) - 1

    def cursor_down(self):
        self.cursor += 1
        if self.cursor >= len(self.state.current_menu.choices):
            self.cursor = 0

    def show_menu(self):
        self.open = True
        self.state.open_menu()
        self.update_menu()

    def close_menu(self):
        self.open = False
        for name, trigger in self.listeners:
            if trigger and name == "close" and callable(trigger):
                trigger()

    def reboot(self):
        self.open = False
        for name, trigger in self.listeners:
            if trigger and name == "reboot" and callable(trigger):
                trigger()

    def shutdown(self):
        self.open = False
        for name, trigger in self.listeners:
            if trigger and name == "shutdown" and callable(trigger):
                trigger()

    def update_menu(self):
        if self.open:
            self.display.display_menu(self.state.current_menu.choices, self.cursor)

    def button_on_click(self, button):
        if not self.open:
            return

        if button == 'a':
            self.cursor = 0
            self.state.select(self.cursor)
            if self.state.current_menu == states.shutdown_menu_state:
                self.shutdown()
                return
            if self.state.current_menu == states.reboot_menu_state:
                self.reboot()
                return
        if button == 'x':
            self.cursor_up()
        if button == 'y':
            self.cursor_down()
        if button == 'b':
            self.cursor = 0
            self.state.go_back()
            if self.state.current_menu == states.close_menu_state:
                self.close_menu()
                return

        # Update the menu
        self.update_menu()
