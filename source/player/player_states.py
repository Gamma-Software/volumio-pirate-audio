from .state import State


class Play(State):
    def run(self):
        print("Play: play the music")

    def next(self):
        return pause


class Stop(State):
    def run(self):
        pass

    def next(self):
        return play


class Pause(State):
    def run(self):
        pass

    def next(self):
        return play


class ChangeMusic(State):
    def run(self):
        pass

    def next(self, input):
        pass


play = Play()
stop = Stop()
pause = Pause()
change_music = ChangeMusic()
