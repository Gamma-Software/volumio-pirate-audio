# StateMachine/StateMachine.py
# Takes a list of Inputs to move from State to
# State using a template method.
from player_states import play_state, stop_state, pause_state, volume_up_state, volume_down_state


class Music:
    def __init__(self, name, artist, album_art, duration):
        self.name = name
        self.artist = artist
        self.album_art = album_art
        self.duration = duration


class MusicQueue:
    def __init__(self):
        self.queue = []

    def add(self, music: Music):
        self.queue.append(music)


class PlayerStateMachine:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.current_volume = 50  # by default the volume is 50%
        self.current_position = 0  # by default the position is 0
        self.music_data = Music()  # TODO
        self.queue = MusicQueue()  # TODO
        self.current_state.run()

    def play_pause(self):
        if self.current_state not in [play_state, pause_state]:
            print("Error: the current state is not play or pause")

        self.current_state = self.current_state.next()
        self.current_state.run()

    def volume_up(self):
        self.current_volume += 10
        if self.current_volume > 100:
            self.current_volume = 100

    def volume_down(self):
        self.current_volume -= 10
        if self.current_volume < 0:
            self.current_volume = 0



