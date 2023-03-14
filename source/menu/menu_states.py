from abc import ABC, abstractmethod

from source.debug import print_debug
from source.utils import MESSAGES_DATA, CONFIG_DATA


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
    def run(self, callback):
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
        self.waiting_for_data = False
        self.choices = []

    def run(self, action_callback):
        self.callback = action_callback
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

    def run(self, callback):
        super().run(callback)
        print(f"Close the menu on {self.close_on}")
        self.callback()

    def next(self, input) -> State:
        self.close_on = None

    def select(self, input):
        return

    def up_down(self, input):
        return

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

    def run(self, callback):
        super().run(callback)

    def next(self, input) -> State:
        choice = self.choices[input]
        if choice not in self.choices:
            raise ValueError("Invalid input")

        if choice == self.messages['DISPLAY']['MUSICSELECTION']:
            return browse_source_menu_state
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


class BrowseLibraryMenu(StateImp):
    def __init__(self, messages):
        super().__init__(messages)
        self.choices = []  # The choices are set in the callback function
        self.waiting_for_data = True
        self.services = []
        self.types = []
        self.uri = []

    def update_choices(self, data):
        list_result = len(data['navigation']['lists'][0]['items'])
        self.services = [data['navigation']['lists'][0]['items'][i]['service'] for i in range(list_result) if 'service' in data['navigation']['lists'][0]['items'][i]]
        self.types = [data['navigation']['lists'][0]['items'][i]['type'] for i in range(list_result)]
        self.choices = [data['navigation']['lists'][0]['items'][i]['title'] for i in range(list_result) if 'title' in data['navigation']['lists'][0]['items'][i]]
        self.uri = [data['navigation']['lists'][0]['items'][i]['uri'] for i in range(list_result) if 'uri' in data['navigation']['lists'][0]['items'][i]]

        self.waiting_for_data = False

    def run(self, callback):
        super().run(callback)
        self.waiting_for_data = True
        self.callback()

    def next(self, input) -> State:
        for types in ['folder', 'radio-', 'streaming-']:
            if types in self.types[input]:
                # We create a new instance of BrowseLibraryMenu with other data
                return BrowseLibraryMenu(MESSAGES_DATA)
        return close_menu_state

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        return browse_source_menu_state


class BrowseSourceMenu(StateImp):
    def __init__(self, messages):
        super().__init__(messages)
        self.choices = []  # The choices are set in the callback function
        self.uri = []
        self.waiting_for_data = True

    def update_choices(self, data):
        self.choices = [data[i]['name'] for i in range(len(data))]
        self.uri = [data[i]['uri'] for i in range(len(data))]
        self.waiting_for_data = False

    def run(self, callback):
        super().run(callback)
        self.waiting_for_data = True
        self.callback()

    def next(self, input) -> State:
        return browse_library_menu_state

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        return main_menu_state


class RebootMenu(StateImp):
    def run(self, callback):
        super().run(callback)
        next(self, 0)  # Close the menu right away

    def next(self, input) -> State:
        return close_menu_state

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        return main_menu_state


class SeekMenu(StateImp):
    def run(self, callback):
        super().run(callback)

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        return main_menu_state


class SleepTimerMenu(StateImp):
    def run(self, callback):
        super().run(callback)

    def next(self, input) -> State:
        return close_menu_state

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        return main_menu_state


class AlarmMenu(StateImp):
    def run(self, callback):
        super().run(callback)

    def next(self, input) -> State:
        return close_menu_state

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        return main_menu_state


class ShutdownMenu(StateImp):
    def run(self, callback):
        super().run(callback)
        next(self, 0)  # Close the menu right away

    def next(self, input) -> State:
        return close_menu_state

    def up_down(self, input):
        pass

    def select(self, input):
        pass

    def previous(self) -> State:
        return main_menu_state


main_menu_state = MainMenu(MESSAGES_DATA)
close_menu_state = MenuClosed(MESSAGES_DATA)
shutdown_menu_state = ShutdownMenu(MESSAGES_DATA)
alarm_menu_state = AlarmMenu(MESSAGES_DATA)
sleep_timer_menu_state = SleepTimerMenu(MESSAGES_DATA)
seek_menu_state = SeekMenu(MESSAGES_DATA)
reboot_menu_state = RebootMenu(MESSAGES_DATA)
browse_source_menu_state = BrowseSourceMenu(MESSAGES_DATA)
browse_library_menu_state = BrowseLibraryMenu(MESSAGES_DATA)
