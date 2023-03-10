from state import State
from player_actions import PlayerAction


class Play(State):
    def run(self):
        print("Play: play the music")

    def next(self, input):
        if input == PlayerAction.pause:
            return PlayerAction.pause
        if input == PlayerAction.stop:
            return PlayerAction.stop
        return PlayerAction.play


class Stop(State):
    def run(self):
        pass

    def next(self, input):
        pass


class Pause(State):
    def run(self):
        pass

    def next(self, input):
        pass


class VolumeUp(State):
    def run(self):
        pass

    def next(self, input):
        pass


class VolumeDown(State):
    def run(self):
        pass

    def next(self, input):
        pass


class ChangeMusic(State):
    def run(self):
        pass

    def next(self, input):
        pass


PlayerAction.play = Play()
PlayerAction.stop = Stop()
PlayerAction.pause = Pause()
PlayerAction.volume_up = VolumeUp()
PlayerAction.volume_down = VolumeDown()
PlayerAction.change_music = ChangeMusic()
