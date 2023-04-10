from source.player.music import Music
from source.debug import print_debug

STATE_PLAY = "play"
STATE_PAUSE = "pause"
STATE_STOP = "stop"


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
        self.music_data = Music(None, None, None, None, None, None, None, None, None)  # TODO
        self.music_changed = False
        self.queue = []

    def parse_player_data(self, data):
        if 'volume' in data:
            self.current_volume = data['volume']

        if 'position' in data:
            self.current_position = data['position']

        if 'status' in data:
            self.status = data['status']

        if 'service' in data:
            self.service = data['service']

    def parse_music_data(self, data, remote_host, remote_port, callback):
        # If the music changed, we reset the music data
        new_music = Music(None, None, None, None, None, None, None, None, callback)

        if 'duration' in data:
            new_music.duration = data['duration']
            if new_music.duration != 0:
                if 'seek' in data and data['seek'] is not None:
                    self.elapsed_time = data['seek']

        if 'title' in data.keys():
            new_music.title = data['title']
        if 'artist' in data.keys():
            new_music.artist = data['artist']
        if 'album' in data.keys():
            new_music.album_name = data['album']
        if 'service' in data.keys():
            new_music.service = data['service']
        if 'type' in data.keys():
            new_music.type = data['type']
        if 'uri' in data.keys():
            new_music.uri = data['uri']
        if 'albumart' in data.keys():
            new_music.album_url = data['albumart']
            if "http" not in new_music.album_url:
                new_music.album_url = ''.join([
                    f'http://{remote_host}:{remote_port}',
                    new_music.album_url.encode('ascii', 'ignore').decode('utf-8')])
            else:  # in case the albumart is already local file
                new_music.album_url = new_music.album_url.encode(
                    'ascii', 'ignore').decode('utf-8')

        if not self.music_data.equal(new_music):
            self.music_changed = True
            self.music_data = new_music.copy()

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
