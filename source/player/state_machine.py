from source.debug import print_debug

STATE_PLAY = "play"
STATE_PAUSE = "pause"
STATE_STOP = "stop"


class Music:
    def __init__(self, name, artist, album_art, album_uri, duration):
        self.name = name
        self.artist = artist
        self.album_art = album_art
        self.album_uri = album_uri
        self.duration = duration


class PlayerStateMachine:
    def __init__(self):
        self.is_playing = False
        self.status = STATE_STOP
        self.service = None
        self.mode = None
        self.last_state = None
        self.current_volume = 50  # by default the volume is 50%
        self.current_position = 0  # by default the position is 0
        self.elapsed_time = 0
        self.music_data = Music(None, None, None, None, None)  # TODO
        self.queue = []

    def parse_data(self, data):
        if 'volume' in data:
            self.current_volume = data['volume']

        if 'position' in data:
            self.current_position = data['position']

        if 'status' in data:
            self.status = data['status']

        if 'service' in data:
            self.service = data['service']

        if 'duration' in data:
            self.duration = data['duration']
            if self.duration != 0:
                if 'seek' in data and data['seek'] is not None:
                    self.elapsed_time = data['seek']

    def play_pause(self):
        if self.status == STATE_PLAY and\
           self.service == 'webradio':
            self.status = STATE_STOP
            print_debug("Stopping webradio")
        elif self.status == STATE_PLAY:
            self.status = STATE_PAUSE
            print_debug("Pausing")
        else:
            self.status = STATE_PLAY
            print_debug("Playing")
        return self.status

    def volume_up(self):
        self.current_volume += 5
        if self.current_volume > 100:
            self.current_volume = 100
        print("Volume: " + str(self.current_volume))

    def volume_down(self):
        self.current_volume -= 5
        if self.current_volume < 0:
            self.current_volume = 0
        print("Volume: " + str(self.current_volume))
