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
        self.current_menu = MenuStateMachine()
        self.display = display
        self.open = False
        self.cursor = 0

    def cursor_up(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = len(self.current_menu.current_menu.choices) - 1

    def cursor_down(self):
        self.cursor += 1
        if self.cursor >= len(self.current_menu.current_menu.choices):
            self.cursor = 0

    def show_menu(self):
        self.open = True
        self.current_menu.open_menu()
        self.update_menu()

    def close_menu(self):
        self.open = False

    def update_menu(self):
        if self.open:
            self.display.display_menu(self.current_menu.current_menu.choices, self.cursor)

    def button_on_click(self, button):
        if not self.open:
            return

        if button == 'a':
            self.cursor = 0
            self.current_menu.select(self.cursor)
        if button == 'x':
            self.cursor_up()
        if button == 'y':
            self.cursor_down()
        if button == 'b':
            self.cursor = 0
            self.current_menu.go_back()
            if self.current_menu.current_menu == states.close_menu_state:
                self.close_menu()

        # Update the menu
        self.update_menu()

        return self.current_menu
