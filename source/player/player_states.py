from state import State
from player_actions import PlayerAction


class Play(State):
    def run(self):
        print("Play: play the music")

    def next(self):
        return PlayerAction.pause


class Stop(State):
    def run(self):
        pass

    def next(self):
        return PlayerAction.play


class Pause(State):
    def run(self):
        pass

    def next(self):
        return PlayerAction.play


class ChangeMusic(State):
    def run(self):
        pass

    def next(self, input):
        pass


play = Play()
stop = Stop()
pause = Pause()
change_music = ChangeMusic()
