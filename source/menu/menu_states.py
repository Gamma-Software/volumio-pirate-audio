class MenuAction:
    def __init__(self, action):
        self.action = action

    def __str__(self): return self.action

    def __cmp__(self, other):
        return cmp(self.action, other.action)

    def __hash__(self):
        return hash(self.action)


class State:
    def run(self):
        assert 0, "run not implemented"

    def next(self, input):
        assert 0, "next not implemented"

    def previous(self):
        assert 0, "previous not implemented"


class MenuClosed(State):
    def run(self):
        print("Close the menu")

    def next(self, input):
        if input == MenuAction.pause:
            return MenuAction.pause
        if input == MenuAction.stop:
            return MenuAction.stop
        return MenuAction.play

    def previous(self):
        assert "cannot go back"


class MainMenu(State):
    def run(self):
        print("Menu: this is the menu")

    def next(self, input):
        return

    def previous(self):
        return close_menu


class BrowseMenu(State):
    def run(self):
        pass

    def next(self, input):
        pass


class RebootMenu(State):
    def run(self):
        pass

    def next(self, input):
        pass


class SeekMenu(State):
    def run(self):
        pass

    def next(self, input):
        pass


class SleepTimerMenu(State):
    def run(self):
        pass

    def next(self, input):
        pass


class AlarmMenu(State):
    def run(self):
        pass

    def next(self, input):
        pass


class ShutdownMenu(State):
    def run(self):
        pass

    def next(self, input):
        pass


main_menu = MainMenu()
close_menu = MenuClosed()
shutdown_menu = ShutdownMenu()
alarm_menu = AlarmMenu()
sleep_timer_menu = SleepTimerMenu()
seek_menu = SeekMenu()
reboot_menu = RebootMenu()
browse_menu = BrowseMenu()
