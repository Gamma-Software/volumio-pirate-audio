from abc import ABC, abstractmethod
from source.utils import MESSAGES_DATA, CONFIG_DATA

from source.debug import print_debug


class MenuAction:
    def __init__(self, action):
        self.action = action

    def __str__(self): return self.action

    def __cmp__(self, other):
        return cmp(self.action, other.action)

    def __hash__(self):
        return hash(self.action)


class State(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def next(self, input):
        pass

    @abstractmethod
    def up_down(self, input):
        pass

    @abstractmethod
    def select(self, input):
        pass

    @abstractmethod
    def previous(self):
        pass


class StateImp(State):
    def __init__(self, messages):
        self.messages = messages
        self.choices = []

    def run(self):
        print_debug("Run -> Menu: " + self.__class__.__name__)
        choices_msg = '\n\t'.join(self.choices)
        print_debug(choices_msg)

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        pass


class MenuClosed(StateImp):
    def __init__(self, messages):
        super().__init__(messages)
        self.close_on: State = None

    def run(self):
        print(f"Close the menu on {self.close_on}")

    def next(self, input) -> State:
        self.close_on = None

    def select(self, input):
        pass

    def up_down(self, input):
        pass

    def previous(self) -> State:
        assert "cannot go back"


class MainMenu(StateImp):
    def __init__(self, messages):
        super().__init__(messages)
        self.choices = [self.messages['DISPLAY']['MUSICSELECTION'],
                        self.messages['DISPLAY']['SEEK'],
                        self.messages['DISPLAY']['PREVNEXT'],
                        'Sleeptimer ' + str(CONFIG_DATA['sleeptimer']['value']) + 'M',
                        self.messages['DISPLAY']['SHUTDOWN'],
                        self.messages['DISPLAY']['REBOOT']]

    def run(self):
        super().run()

    def next(self, input) -> State:
        choice = self.choices[input]
        if choice not in self.choices:
            raise ValueError("Invalid input")

        if choice == self.messages['DISPLAY']['MUSICSELECTION']:
            print("Not implemented yet")
            #return BrowseMenu(self.messages)
            return
        if choice == self.choices[1]:  # seek
            return seek_menu_state
        if choice == self.choices[2]:  # next/previous music
            return seek_menu_state
        if choice == self.choices[3]:  # sleeptimer
            return sleep_timer_menu_state
        if choice == self.choices[4]:  # shutdown
            return shutdown_menu_state
        if choice == self.choices[5]:  # reboot
            return reboot_menu_state

    def select(self, input):
        pass

    def up_down(self, input):
        pass

    def previous(self) -> State:
        return close_menu_state


class BrowseMenu(StateImp):
    def __init__(self, messages):
        super().__init__(messages)
        self.choices = []  # The choices are set in the callback function

    def update_choices(self, data):
        self.choices = [data[0][i]['name']
                        for i in range(len(data[0]))]

    def run(self):
        super().run()

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        pass


class RebootMenu(StateImp):
    def run(self):
        super().run()

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        pass


class SeekMenu(StateImp):
    def run(self):
        super().run()

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        pass


class SleepTimerMenu(StateImp):
    def run(self):
        super().run()

    def next(self, input) -> State:
        return close_menu_state

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        pass


class AlarmMenu(StateImp):
    def run(self):
        super().run()

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        pass


class ShutdownMenu(StateImp):
    def run(self):
        super().run()
        next(self, 0)  # Close the menu right away

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        pass


main_menu_state = MainMenu(MESSAGES_DATA)
close_menu_state = MenuClosed(MESSAGES_DATA)
shutdown_menu_state = ShutdownMenu(MESSAGES_DATA)
alarm_menu_state = AlarmMenu(MESSAGES_DATA)
sleep_timer_menu_state = SleepTimerMenu(MESSAGES_DATA)
seek_menu_state = SeekMenu(MESSAGES_DATA)
reboot_menu_state = RebootMenu(MESSAGES_DATA)
browse_menu_state = BrowseMenu(MESSAGES_DATA)
