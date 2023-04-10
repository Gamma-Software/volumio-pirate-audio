import time
from datetime import datetime
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
    def run(self, socket):
        pass

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def up_down(self, input):
        pass

    @abstractmethod
    def select(self):
        pass


class StateImp(State):
    def __init__(self, messages, socket, display):
        self.messages = messages
        self.waiting_for_data = False
        self.choices = []
        self.socket = socket
        self.display = display
        self.cursor = 0

    def run(self):
        # print_debug("Run -> Menu: " + self.__class__.__name__)
        pass

    def next(self) -> State:
        pass

    def up_down(self, input):
        if self.choices == []:
            # print_debug("No choices available, cannot move cursor")
            return
        if input == "up":
            self.cursor -= 1
            if self.cursor < 0:
                self.cursor = len(self.choices) - 1
        elif input == "down":
            self.cursor += 1
            if self.cursor >= len(self.choices):
                self.cursor = 0

    def select(self):
        pass


class MenuClosed(StateImp):
    def __init__(self, close_on: State, messages, socket, display):
        super().__init__(messages, socket, display)
        self.close_on: str = close_on.__name__

    def run(self):
        super().run()
        print(f"Close the menu on {self.close_on}")

    def next(self) -> State:
        self.close_on = None

    def select(self):
        return

    def up_down(self, input):
        super().up_down(input)


class MainMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)
        self.choices = [self.messages['DISPLAY']['MUSICSELECTION'],
                        self.messages['DISPLAY']['SEEK'],
                        self.messages['DISPLAY']['PREVNEXT'],
                        'Sleeptimer ' + str(CONFIG_DATA['sleeptimer']['value']) + 'M',
                        "Alarm",
                        self.messages['DISPLAY']['SHUTDOWN'],
                        self.messages['DISPLAY']['REBOOT']]
        # print_debug("Choices: \n\t" + "\n\t".join(self.choices))

    def run(self):
        super().run()
        self.display.display_menu_content(self.choices, self.cursor)

    def next(self) -> State:
        choice = self.choices[self.cursor]
        if choice not in self.choices:
            raise ValueError("Invalid input")

        if choice == self.messages['DISPLAY']['MUSICSELECTION']:
            return BrowseSourceMenu(MESSAGES_DATA, self.socket, self.display)
        if choice == self.choices[1]:  # seek
            return SeekMenu(MESSAGES_DATA, self.socket, self.display)
        if choice == self.choices[2]:  # prevnext
            return PrevNextMenu(MESSAGES_DATA, self.socket, self.display)
        if choice == self.choices[3]:  # sleeptimer
            return SleepTimerMenu(MESSAGES_DATA, self.socket, self.display)
        if choice == self.choices[4]:  # Alarm
            return AlarmMenu(MESSAGES_DATA, self.socket, self.display)
        if choice == self.choices[5]:  # shutdown
            return ShutdownMenu(MESSAGES_DATA, self.socket, self.display)
        if choice == self.choices[6]:  # reboot
            return RebootMenu(MESSAGES_DATA, self.socket, self.display)

    def select(self):
        pass

    def up_down(self, input):
        super().up_down(input)
        self.display.display_menu_content(self.choices, self.cursor)


class BrowseLibraryMenu(StateImp):
    def __init__(self, selected_uri, messages, socket, display):
        super().__init__(messages, socket, display)
        self.choices = []  # The choices are set in the socket function
        self.waiting_for_data = True
        self.services = []
        self.types = []
        self.uri = []
        self.selected_uri = selected_uri
        self.socket.on('pushBrowseLibrary', self.update_data)

    def update_data(self, data):
        data_filtered = data['navigation']['lists'][0]

        for data in data_filtered['items']:
            self.types.append(data['type'])
            if 'service' in data:
                self.services.append(data['service'])
            if 'title' in data:
                self.choices.append(data['title'])
            if 'uri' in data:
                self.uri.append(data['uri'])

        self.display.display_menu_content(self.choices, self.cursor)
        # print_debug("Choices: \n\t" + "\n\t".join(self.choices))

    def run(self):
        super().run()
        self.socket.emit('browseLibrary', {'uri': self.selected_uri})

    def next(self) -> State:
        uri = self.uri[self.cursor]
        if self.types != []:
            for types in ['folder', 'radio-', 'streaming-']:
                if types in self.types[self.cursor]:
                    uri = uri.replace('mnt/', 'music-library/')
                    return BrowseLibraryMenu(uri, MESSAGES_DATA, self.socket, self.display)
            if self.types[self.cursor] in ['song', 'webradio', 'mywebradio']:
                service = self.services[self.cursor]
                name = self.choices[self.cursor]
                type = self.types[self.cursor]
                uri = self.uri[self.cursor]
                if type == 'playlist':
                    if service == 'mpd':
                        self.socket.emit('playPlaylist', {'name': name})
                        return
                    if service == 'spop':
                        self.socket.emit('stop')
                        time.sleep(2)
                print("PLAY -> service: " + service + " type: " + type +
                      " name: " + name + " uri: " + uri)
                self.socket.emit('replaceAndPlay', {
                    "service": service, "type":
                    type, "title": name,
                    "uri": uri})
                return MenuClosed(BrowseLibraryMenu, MESSAGES_DATA, self.socket, self.display)
        return BrowseLibraryMenu(uri, MESSAGES_DATA, self.socket, self.display)

    def up_down(self, input):
        super().up_down(input)
        self.display.display_menu_content(self.choices, self.cursor)

    def select(self):
        pass


class BrowseSourceMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)
        self.choices = []  # The choices are set in the socket function
        self.uri = []
        self.socket.on('pushBrowseSources', self.update_data)

    def update_data(self, data):
        self.choices = [data[i]['name'] for i in range(len(data))]
        self.uri = [data[i]['uri'] for i in range(len(data))]
        self.display.display_menu_content(self.choices, self.cursor)
        # print_debug("Choices: \n\t" + "\n\t".join(self.choices))

    def run(self):
        super().run()
        self.socket.emit('getBrowseSources', '', self.update_data)

    def next(self) -> State:
        return BrowseLibraryMenu(self.uri[self.cursor], MESSAGES_DATA, self.socket, self.display)

    def up_down(self, input):
        super().up_down(input)
        self.display.display_menu_content(self.choices, self.cursor)

    def select(self):
        pass


class SeekMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)
        self.current_duration = None
        self.seek = None
        self.no_seek = False
        self.socket.on('pushState', self.update_duration)

    def update_display(self):
        if self.no_seek:
            self.display.display_menu_content(MESSAGES_DATA['DISPLAY']['NO_SEEK'], 0, 'info')
            return
        seek_msg = time.strftime("%M:%S", time.gmtime(
            int(float(self.seek/1000))))
        duration_msg = time.strftime("%M:%S", time.gmtime(
            self.current_duration))

        self.display.display_menu_content([MESSAGES_DATA['DISPLAY']['SEEK'],
                                           ''.join([seek_msg, ' / ', duration_msg])],
                                          self.cursor, 'seek')

    def update_duration(self, data):
        if 'duration' not in data:
            return
        if 'service' in data and data['service'] == 'webradio':
            self.no_seek = True
        self.current_duration = data['duration']
        if self.current_duration != 0:
            if 'seek' in data and data['seek'] is not None:
                self.seek = data['seek']
        self.update_display()

    def run(self):
        super().run()
        # Update data
        self.socket.emit('getState', '', self.update_duration)

    def next(self) -> State:
        self.socket.emit('seek', int(float(self.seek/1000)))
        return MenuClosed(SeekMenu, MESSAGES_DATA, self.socket, self.display)

    def up_down(self, input):
        super().up_down(input)
        if not self.current_duration and not self.seek or self.no_seek:
            return
        step = 30000  # 30 seconds
        if input == 'up':
            if int(float((self.seek + step)/1000)) < self.current_duration:
                self.seek += step
        elif input == 'down':
            if int(float((self.seek - step)/1000)) > 0:
                self.seek -= step

        if int(float(self.seek/1000)) > self.current_duration:
            self.seek = self.current_duration * 1000
        if int(float(self.seek/1000)) < 0:
            self.seek = 0

        self.update_display()

    def select(self):
        pass


class PrevNextMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)
        self.choices = []
        self.socket.on('pushQueue', self.update_data)

    def update_data(self, data):
        self.choices = [d['name'] for d in data]
        if len(self.choices) <= 1:
            self.display.display_menu_content(MESSAGES_DATA['DISPLAY']['NO_QUEUE'], 0, 'info')
            return
        self.display.display_menu_content(self.choices, 0, 'seek')
        # print_debug("Choices: \n\t" + "\n\t".join(self.choices))

    def run(self):
        super().run()
        self.waiting_for_data = True
        self.socket.emit('getQueue', self.update_data)

    def next(self) -> State:
        """processes prev/next commands"""
        if self.waiting_for_data:
            return None
        next_state = MenuClosed(PrevNextMenu, MESSAGES_DATA, self.socket, self.display)
        if len(self.choices) > 1:
            self.socket.emit('stop')
            self.socket.emit('play', {"value": self.choices[self.cursor]})
        return next_state

    def up_down(self, input):
        super().up_down(input)
        if len(self.choices) <= 1:
            return
        self.display.display_menu_content(self.choices, self.cursor, 'seek')

    def select(self):
        pass


class SleepTimerMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)

    def run(self):
        super().run()
        self.display.display_menu_content(self.choices, self.cursor)

    def next(self) -> State:
        return MenuClosed(SleepTimerMenu, MESSAGES_DATA, self.socket, self.display)

    def up_down(self, input):
        super().up_down(input)
        self.display.display_menu_content(self.choices, self.cursor)

    def select(self):
        pass


class AlarmMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)
        self.waiting_for_data = True
        self.socket.on('pushAlarm', self.update_data)
        self.choices = ["Add alarm [+]"]

    def update_data(self, data):
        # Parse the time data from YYYY-MM-DDTHH:MM:SSZ to HH:MM
        for alarm in data:
            # Parse the string into a datetime object
            time_obj = datetime.fromisoformat(alarm['time'][:-1])

            # Extract the hour and minute from the datetime object
            hour = time_obj.hour
            minute = time_obj.minute
            self.choices.insert(0, f'{hour}:{minute}')
        self.display.display_menu_content(self.choices, self.cursor)

        self.waiting_for_data = False

    def run(self):
        super().run()
        self.waiting_for_data = True
        self.socket.emit('getAlarms', self.update_data)
        self.display.display_menu_content(self.choices, self.cursor)

    def next(self) -> State:
        if self.waiting_for_data:
            return None
        return MenuClosed(AlarmMenu, MESSAGES_DATA, self.socket, self.display)

    def up_down(self, input):
        super().up_down(input)
        if self.waiting_for_data:
            return None
        self.display.display_menu_content(self.choices, self.cursor)

    def select(self):
        pass

class AlarmSubMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)
        self.waiting_for_data = True
        self.socket.on('pushAlarm', self.update_data)
        self.choices = ["Add alarm [+]"]

    def update_data(self, data):
        # Parse the time data from YYYY-MM-DDTHH:MM:SSZ to HH:MM
        for alarm in data:
            # Parse the string into a datetime object
            time_obj = datetime.fromisoformat(alarm['time'][:-1])

            # Extract the hour and minute from the datetime object
            hour = time_obj.hour
            minute = time_obj.minute
            self.choices.insert(0, f'{hour}:{minute}')
        self.display.display_menu_content(self.choices, self.cursor)

        self.waiting_for_data = False

    def run(self):
        super().run()
        self.waiting_for_data = True
        self.socket.emit('getAlarms', self.update_data)
        self.display.display_menu_content(self.choices, self.cursor)

    def next(self) -> State:
        if self.waiting_for_data:
            return None
        return MenuClosed(AlarmMenu, MESSAGES_DATA, self.socket, self.display)

    def up_down(self, input):
        super().up_down(input)
        if self.waiting_for_data:
            return None
        self.display.display_menu_content(self.choices, self.cursor)

    def select(self):
        pass


class RebootMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)
        self.choices = [self.messages['DISPLAY']['REBOOT'], self.messages['DISPLAY']['CANCEL']]
        # print_debug("Choices: \n\t" + "\n\t".join(self.choices))

    def run(self):
        super().run()
        self.display.display_menu_content(self.choices, self.cursor)

    def next(self) -> State:
        # Trick: if the user cancels (input == 1), the menu is closed without rebooting
        if self.cursor == 1:
            return MenuClosed(MainMenu, MESSAGES_DATA, self.socket, self.display)

        self.socket.emit('reboot')
        self.display.display_reboot()
        return MenuClosed(RebootMenu, MESSAGES_DATA, self.socket, self.display)

    def up_down(self, input):
        super().up_down(input)
        self.display.display_menu_content(self.choices, self.cursor)

    def select(self):
        pass


class ShutdownMenu(StateImp):
    def __init__(self, messages, socket, display):
        super().__init__(messages, socket, display)
        self.choices = [self.messages['DISPLAY']['SHUTDOWN'], self.messages['DISPLAY']['CANCEL']]
        # print_debug("Choices: \n\t" + "\n\t".join(self.choices))

    def run(self):
        super().run()
        self.display.display_menu_content(self.choices, self.cursor)

    def next(self) -> State:
        # Trick: if the user cancels (input == 1), the menu is closed without rebooting
        if self.cursor == 1:
            return MenuClosed(MainMenu, MESSAGES_DATA, self.socket, self.display)

        self.socket.emit('shutdown')
        self.display.display_shutdown()
        return MenuClosed(ShutdownMenu, MESSAGES_DATA,
                          self.socket, self.display)

    def up_down(self, input):
        super().up_down(input)
        self.display.display_menu_content(self.choices, self.cursor)

    def select(self):
        pass
