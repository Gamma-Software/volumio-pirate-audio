import requests
from io import BytesIO
from PIL import Image
from source.debug import print_debug


class Music:
    def __init__(self, title, artist, album_name, album_url, duration, callback):
        self.title = title
        self.artist = artist
        self.album_name = album_name
        self.album_image = None
        self.album_url = album_url
        self.need_to_be_updated = False
        self.duration = duration
        self.callback = callback

    def copy(self):
        return Music(self.title, self.artist, self.album_name,
                     self.album_url, self.duration, self.callback)

    def equal(self, other):
        return self.title == other.title

    def download_album_image(self, screen_size):
        print_debug(f"Downloading album art from {self.album_url}")
        if self.album_url is not None:
            try:
                response = requests.get(self.album_url)
                if response.status_code == 200:
                    self.album_image = Image.open(BytesIO(response.content)).convert('RGBA')
                    self.album_image = self.album_image.resize(screen_size)
                    self.need_to_be_updated = True
                    self.callback()
            except Exception as e:
                print_debug(f"Error while downloading album art: {e}")
                self.album_image = None
