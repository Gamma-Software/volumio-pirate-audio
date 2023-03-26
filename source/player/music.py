import requests
from io import BytesIO
from PIL import Image, ImageFilter
from source.debug import print_debug


class Music:
    def __init__(self, title, artist, album_name, album_url, duration):
        if "http" not in album_url:
            self.album_url = ''.join([f'http://{self.remote_host}:{self.remote_port}',
                                      album_url.encode('ascii', 'ignore').decode('utf-8')])
        else:  # in case the albumart is already local file
            self.album_url = album_url.encode('ascii', 'ignore').decode('utf-8')
        self.title = title
        self.artist = artist
        self.album_name = album_name
        self.album_image = None
        self.duration = duration

    def copy(self):
        return Music(self.title, self.artist, self.album_name, self.album_url, self.duration)

    def download_album_image(self, screen_size):
        if self.album_art is not None:
            try:
                response = requests.get(self.album_art, stream=True)
                if response.status_code == 200:
                    self.album_image = Image.open(BytesIO(response.content))
                    self.album_image = self.album_image.resize(screen_size)
                    self.album_image = self.album_image.filter(ImageFilter.BLUR)  # Blur
            except Exception as e:
                print_debug("Error while downloading album art: {}".format(e))
                self.album_image = None
