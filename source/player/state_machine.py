# StateMachine/StateMachine.py
# Takes a list of Inputs to move from State to
# State using a template method.

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



