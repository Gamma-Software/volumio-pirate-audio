import time
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
    def next(self, input):
        pass

    @abstractmethod
    def up_down(self, input):
        pass

    @abstractmethod
    def select(self, input):
        pass


class StateImp(State):
    def __init__(self, messages, socket, on_push_browsesources, on_push_browselibrary):
        self.messages = messages
        self.waiting_for_data = False
        self.choices = []
        self.socket = socket
        self.on_push_browsesources = on_push_browsesources
        self.on_push_browselibrary = on_push_browselibrary

    def run(self):
        print_debug("Run -> Menu: " + self.__class__.__name__)

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass


class MenuClosed(StateImp):
    def __init__(self, close_on, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)
        self.close_on: State = close_on

    def run(self):
        super().run()
        print(f"Close the menu on {self.close_on}")

    def next(self, input) -> State:
        self.close_on = None

    def select(self, input):
        return

    def up_down(self, input):
        return


class MainMenu(StateImp):
    def __init__(self, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)
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
            return BrowseSourceMenu(MESSAGES_DATA, self.socket,
                                    self.on_push_browsesources, self.on_push_browselibrary)
        if choice == self.choices[1]:  # seek
            return SeekMenu(MESSAGES_DATA, self.socket,
                            self.on_push_browsesources, self.on_push_browselibrary)

        if choice == self.choices[3]:  # sleeptimer
            return SleepTimerMenu(MESSAGES_DATA, self.socket,
                                  self.on_push_browsesources, self.on_push_browselibrary)
        if choice == self.choices[4]:  # shutdown
            return ShutdownMenu(MESSAGES_DATA, self.socket,
                                self.on_push_browsesources, self.on_push_browselibrary)
        if choice == self.choices[5]:  # reboot
            return RebootMenu(MESSAGES_DATA, self.socket,
                              self.on_push_browsesources, self.on_push_browselibrary)

    def select(self, input):
        pass

    def up_down(self, input):
        pass


class BrowseLibraryMenu(StateImp):
    def __init__(self, selected_uri, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)
        self.choices = []  # The choices are set in the socket function
        self.waiting_for_data = True
        self.services = []
        self.types = []
        self.uri = []
        self.selected_uri = selected_uri

    def update_choices(self, data):
        data_filtered = data['navigation']['lists'][0]

        for data in data_filtered['items']:
            self.types.append(data['type'])
            if 'service' in data:
                self.services.append(data['service'])
            if 'title' in data:
                self.choices.append(data['title'])
            if 'uri' in data:
                self.uri.append(data['uri'])

        self.waiting_for_data = False

    def run(self):
        super().run()
        self.waiting_for_data = True
        self.socket.emit('browseLibrary', {'uri': self.selected_uri})

    def next(self, input) -> State:
        uri = self.uri[input]
        if self.types != []:
            for types in ['folder', 'radio-', 'streaming-']:
                if types in self.types[input]:
                    uri = uri.replace('mnt/', 'music-library/')
                    return BrowseLibraryMenu(uri, MESSAGES_DATA, self.socket,
                                             self.on_push_browsesources,
                                             self.on_push_browselibrary)
            if self.types[input] in ['song', 'webradio', 'mywebradio']:
                service = self.services[input]
                name = self.choices[input]
                type = self.types[input]
                uri = self.uri[input]
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
                return MenuClosed(BrowseLibraryMenu, MESSAGES_DATA, self.socket,
                                  self.on_push_browsesources, self.on_push_browselibrary)
        return BrowseLibraryMenu(uri, MESSAGES_DATA, self.socket,
                                 self.on_push_browsesources,
                                 self.on_push_browselibrary)

    def up_down(self, input):
        pass

    def select(self, input):
        pass


class BrowseSourceMenu(StateImp):
    def __init__(self, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)
        self.choices = []  # The choices are set in the socket function
        self.uri = []
        self.waiting_for_data = True

    def update_choices(self, data):
        self.choices = [data[i]['name'] for i in range(len(data))]
        self.uri = [data[i]['uri'] for i in range(len(data))]
        self.waiting_for_data = False

    def run(self):
        super().run()
        self.waiting_for_data = True
        self.socket.emit('getBrowseSources', '', self.on_push_browsesources)

    def next(self, input) -> State:
        return BrowseLibraryMenu(self.uri[input], MESSAGES_DATA, self.socket,
                                 self.on_push_browsesources, self.on_push_browselibrary)

    def up_down(self, input):
        pass

    def select(self, input):
        pass


class RebootMenu(StateImp):
    def __init__(self, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)

    def run(self):
        super().run()
        next(self, 0)  # Close the menu right away

    def next(self, input) -> State:
        return MenuClosed(RebootMenu, MESSAGES_DATA, self.socket,
                          self.on_push_browsesources, self.on_push_browselibrary)

    def up_down(self, input):
        pass

    def select(self, input):
        pass


class SeekMenu(StateImp):
    def __init__(self, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)

    def run(self):
        super().run()

    def next(self, input) -> State:
        pass

    def up_down(self, input):
        pass

    def select(self, input):
        pass


class SleepTimerMenu(StateImp):
    def __init__(self, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)

    def run(self):
        super().run()

    def next(self, input) -> State:
        return MenuClosed(SleepTimerMenu, MESSAGES_DATA, self.socket,
                          self.on_push_browsesources, self.on_push_browselibrary)

    def up_down(self, input):
        pass

    def select(self, input):
        pass


class AlarmMenu(StateImp):
    def __init__(self, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)

    def run(self):
        super().run()

    def next(self, input) -> State:
        return MenuClosed(AlarmMenu, MESSAGES_DATA, self.socket,
                          self.on_push_browsesources, self.on_push_browselibrary)

    def up_down(self, input):
        pass

    def select(self, input):
        pass


class ShutdownMenu(StateImp):
    def __init__(self, messages, socket, on_push_browsesources, on_push_browselibrary):
        super().__init__(messages, socket, on_push_browsesources, on_push_browselibrary)

    def run(self):
        super().run()
        next(self, 0)  # Close the menu right away

    def next(self, input) -> State:
        return MenuClosed(ShutdownMenu, MESSAGES_DATA, self.socket,
                          self.on_push_browsesources, self.on_push_browselibrary)

    def up_down(self, input):
        pass

    def select(self, input):
        pass
