import threading
from source.player.music import Music
from source.hardware.draw_utils import DrawUtils, ScreenData, OverlayData
from source.debug import check_perfo
from time import time
from PIL import Image, ImageDraw, ImageStat, ImageFilter

from source import SIMULATOR

if SIMULATOR:
    import source.simulator.ST7789 as ST7789  # simulator
else:
    import ST7789


class DisplayHandler:
    def __init__(self, fonts, messages, time_to_sleep=60, max_list=5) -> None:
        self.fonts = fonts
        self.messages = messages

        # screen
        self.last_refresh = time()
        self.max_list = max_list
        self.screen = ScreenData()
        self.overlay = OverlayData()
        self.draw_utils = DrawUtils(fonts, self.screen, self.overlay)

        self.default_background = Image.open('images/default.jpg').resize(
            (self.screen.width, self.screen.height))
        self.static_menu_image = None
        self.static_player_image = None
        self.dynamic_image = self.default_background.copy()
        self.last_menu_image = self.default_background.copy()
        self.last_player_image = self.default_background.copy()

        self.display = ST7789.ST7789(
            height=self.screen.width,
            width=self.screen.height,
            rotation=90,  # Needed to display the right way up on Pirate Audio
            port=0,       # SPI port
            cs=1,         # SPI port Chip-select channel
            dc=9,         # BCM pin used for data/command
            backlight=13,
            spi_speed_hz=80 * 1000 * 1000,
            offset_left=0,
            offset_top=0
        )

    def clean(self):
        pass

    def display_connect(self):
        """display connect"""
        self.display.set_backlight(True)
        self.display_menu(self.messages['DISPLAY']['WAIT'], 0, 0, 'info')

    def display_disconnect(self):
        """display disconnect"""
        self.display.set_backlight(True)
        self.display_menu(self.messages["DISPLAY"]['LOSTCONNECTION'], 0, 0, 'info')

    def display_menu_content(self, menu_list, cursor, icon='nav'):
        """display menu"""
        self.display.set_backlight(True)

        if len(menu_list) == 0:
            menu_list = self.messages['DISPLAY']['EMPTY']
        self.display_menu(menu_list, cursor, cursor, icon)

    def display_shutdown(self):
        self.display.set_backlight(True)
        # TODO : add a shutdown message
        self.display_menu(['executing:', 'shutdown'], 0, 0, 'info')

    def display_reboot(self):
        self.display.set_backlight(True)
        # TODO : add a reboot message
        self.display_menu(['executing:', 'reboot'], 0, 0, 'info')

    def refresh(self):
        pass

    def sendtodisplay(self, image_to_display: Image):
        """send img to display"""
        self.last_refresh = time()
        self.display.display(image_to_display._image)

    @check_perfo
    def display_player(self, music_data: Music, current_volume, status, current_position,
                       redraw_static=False, use_last_image=False):
        if use_last_image:
            self.sendtodisplay(self.last_player_image)
            return

        # Draw static elements only if needed
        if redraw_static or music_data.need_to_be_updated:
            # This is the canvas on which we will draw.
            # (the current image is the default background or the album image)
            if music_data.album_image:
                self.static_player_image = ImageDraw.Draw(
                    music_data.album_image.filter(ImageFilter.BLUR).copy(), 'RGBA')  # Blur
                im_stat = ImageStat.Stat(self.static_player_image._image)
                self.overlay.update_contrast_overlay(im_stat)
                music_data.need_to_be_updated = False
            else:
                # If their is a music playing but no album image we start a thread to download it
                if music_data.title and music_data.album_image is None:
                    threading.Thread(target=music_data.download_album_image,
                                     args=((self.screen.width, self.screen.height), )).start()
                self.static_player_image = ImageDraw.Draw(
                    self.default_background.filter(ImageFilter.BLUR).copy(), 'RGBA')

        # Draw first the background with static elements such as
        # the title and the album name and the artist name and the menu button
        self.draw_utils.draw_static_player_overlay(self.static_player_image, music_data)

        # Then draw the dynamic elements such as the volume bar and the time bar
        self.dynamic_image = ImageDraw.Draw(self.static_player_image._image.copy(), 'RGBA')
        self.draw_utils.draw_status_overlay(self.dynamic_image, status)
        self.draw_utils.draw_volume_overlay(self.dynamic_image, current_volume)
        self.draw_utils.draw_timebar(self.dynamic_image, current_position, music_data.duration)

        self.sendtodisplay(self.dynamic_image)
        self.last_player_image = self.dynamic_image._image.copy()

    @check_perfo
    def display_menu(self, choices, marked, start, icons='nav', redraw_static=False,
                     use_last_image=False):
        # If choices is a string, we convert it to a list
        if isinstance(choices, str):
            choices = [choices]
        if use_last_image:
            self.sendtodisplay(self.last_player_image)
            return

        # Draw static elements
        # This is the canvas on which we will draw.
        # (the current image is the default background or the album image)
        self.static_menu_image = ImageDraw.Draw(self.default_background.copy(), 'RGBA')

        # Draw first the background with static elements such as the symbols
        if icons == 'nav':
            # Fontawesome symbol ok
            self.draw_utils.draw_symbol(self.static_menu_image, 0, 50, u"\uf14a")
            # Fontawesome symbol up
            self.draw_utils.draw_symbol(self.static_menu_image, 210, 50, u"\uf151")
            # Fontawesome symbol back
            self.draw_utils.draw_symbol(self.static_menu_image, 0, 170, u"\uf0e2")
            # Fontawesome symbol down
            self.draw_utils.draw_symbol(self.static_menu_image, 210, 170, u"\uf150")
        elif icons == 'info':
            # Fontawesome symbol info
            self.draw_utils.draw_symbol(self.static_menu_image, 10, 10, u"\uf05a")
            # Fontawesome symbol back
            self.draw_utils.draw_symbol(self.static_menu_image, 0, 170, u"\uf0e2")
        elif icons == 'seek':
            # Fontawesome symbol ok
            self.draw_utils.draw_symbol(self.static_menu_image, 0, 50, u"\uf14a")
            # Fontawesome symbol forward
            self.draw_utils.draw_symbol(self.static_menu_image, 210, 50, u"\uf04e")
            # Fontawesome symbol back
            self.draw_utils.draw_symbol(self.static_menu_image, 0, 170, u"\uf0e2")
            # Fontawesome symbol backward
            self.draw_utils.draw_symbol(self.static_menu_image, 210, 170, u"\uf04a")

        # Then draw the dynamic elements such as the menu content
        self.dynamic_image = ImageDraw.Draw(self.static_menu_image._image.copy(), 'RGBA')
        self.draw_utils.draw_menu_content(self.dynamic_image, choices, start, marked, self.max_list)
        self.draw_utils.draw_page_indicator(self.dynamic_image, marked, len(choices), self.max_list)

        self.sendtodisplay(self.dynamic_image)
        self.last_menu_image = self.dynamic_image._image.copy()
