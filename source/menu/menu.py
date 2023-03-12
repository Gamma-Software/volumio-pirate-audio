import source.menu.menu_states as states


class MenuStateMachine:
    def __init__(self):
        self.current_menu = None
        self.main_menu()

    def main_menu(self):
        self.current_menu = states.main_menu
        self.current_menu.run()

    def select(self, menu_selected):
        self.current_menu = self.current_menu.next(menu_selected)
        self.current_menu.run()

    def go_back(self) -> bool:
        if self.current_menu == states.close_menu:
            print("Error: cannot go back")
            return

        self.current_menu = self.current_menu.previous()
        self.current_menu.run()


class Menu:
    def __init__(self, max_menu_list, sleeptimer) -> None:
        self.state = MenuStateMachine()
        self.open = False
        self.cursor = 0
        self.max_menu_list = max_menu_list
        self.sleeptimer = sleeptimer

    def cursor_up(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = len(self.state.current_menu.content)

    def cursor_down(self):
        self.cursor += 1
        if self.cursor > len(self.state.current_menu.content):
            self.cursor = 0

    def button_on_click(self, button):
        if not self.open:
            return

        if button == 'a':
            self.state.select()
        if button == 'x':
            self.cursor_up()
        if button == 'y':
            self.cursor_down()
        if button == 'b':
            self.state.go_back()

    def close_menu(self):
        self.open = False
        self.cursor = 0

    def show_menu(self):
        self.open = True
        self.state.main_menu()
