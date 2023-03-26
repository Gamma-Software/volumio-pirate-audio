from source.debug import print_debug

STATE_PLAY = "play"
STATE_PAUSE = "pause"
STATE_STOP = "stop"


class Music:
    def __init__(self, title, artist, album_name, album_art, album_url, duration):
        self.title = title
        self.artist = artist
        self.album_name = album_name
        self.album_art = album_art
        self.album_url = album_url
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
        self.music_data = Music(None, None, None, None, None, None)  # TODO
        self.last_music_data = Music(None, None, None, None, None, None)  # TODO
        self.music_changed = False
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
            self.music_data.duration = data['duration']
            if self.music_data.duration != 0:
                if 'seek' in data and data['seek'] is not None:
                    self.elapsed_time = data['seek']

        if 'title' in data.keys():
            self.music_data.title = data['title']
        if 'artist' in data.keys():
            self.music_data.artist = data['artist']
        if 'album' in data.keys():
            self.music_data.album_name = data['album']
        if 'albumart' in data.keys():
            self.music_data.album_art = data['albumart']
        if 'uri' in data.keys():
            self.music_data.album_url = data['uri']

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

    def volume_down(self):
        self.current_volume -= 5
        if self.current_volume < 0:
            self.current_volume = 0