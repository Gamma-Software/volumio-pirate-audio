from source.hardware.draw_utils import DrawUtils
from source.hardware.draw_utils import ScreenData, ScreenSleepData, OverlayData
from source.debug import check_perfo
from time import time
from PIL import ImageDraw, ImageStat, ImageFilter

from source import SIMULATOR

if SIMULATOR:
    import source.simulator.ST7789 as ST7789  # simulator
else:
    import ST7789


class DisplayHandler:
    def __init__(self, fonts, messages, time_to_sleep=60, max_list=5) -> None:
        self.fonts = fonts
        self.messages = messages
        self.draw_utils = DrawUtils(fonts, self.screen, self.overlay)

        # screen
        self.max_list = max_list
        self.sleep = ScreenSleepData(time_to_sleep)
        self.screen = ScreenData()

        # overlay
        self.overlay = OverlayData()

        self.display = ST7789.ST7789(
            height=240,
            width=240,
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
        self.display_menu(self.screen.default_background,
                          self.messages['DISPLAY']['WAIT'], 0, 0, 'info')

    def display_disconnect(self):
        """display disconnect"""
        self.display.set_backlight(True)
        self.display_menu(self.screen.default_background,
                          self.messages["DISPLAY"]['LOSTCONNECTION'], 0, 0, 'info')

    def display_menu_content(self, menu_list, cursor, icon='nav'):
        """display menu"""
        self.display.set_backlight(True)

        if len(menu_list) == 0:
            menu_list = self.messages['DISPLAY']['EMPTY']
        self.display_menu(self.screen.default_background,
                          menu_list, cursor, cursor, icon)

    def display_shutdown(self):
        self.display.set_backlight(True)
        # TODO : add a shutdown message
        self.display_menu(self.screen.default_background,
                          ['executing:', 'shutdown'], 0, 0, 'info')

    def display_reboot(self):
        self.display.set_backlight(True)
        # TODO : add a reboot message
        self.display_menu(self.screen.default_background,
                          ['executing:', 'reboot'], 0, 0, 'info')

    def refresh(self):
        pass

    def sendtodisplay(self, image_to_display):
        """send img to display"""
        self.screen.last_refresh = time()
        self.display(image_to_display)

    @check_perfo
    def display_player(self, music_data, current_volume, status, current_position,
                       redraw_static=False, use_last_image=False):
        if use_last_image:
            self.sendtodisplay(self.screen.last_player_image)
            return

        # Draw static elements only if needed
        if redraw_static or self.static_image is None:
            # This is the canvas on which we will draw.
            # (the current image is the default background or the album image)
            if music_data.album_image:
                self.static_image = music_data.album_image.filter(ImageFilter.BLUR)  # Blur
                im_stat = ImageStat.Stat(self.static_image)
                self.overlay.update_contrast_overlay(im_stat)
            else:
                self.static_image = ImageDraw.Draw(self.screen.default_background, 'RGBA')

            # Draw first the background with static elements such as
            # the title and the album name and the artist name and the menu button
            self.draw_utils.draw_overlay(self.static_image, status, current_volume, music_data)

        # Then draw the dynamic elements such as the volume bar and the time bar
        self.dynamic_image = self.static_image.copy()
        self.draw_utils.draw_volume_overlay(self.dynamic_image, current_volume)
        self.draw_utils.draw_timebar(self.dynamic_image, current_position, music_data.duration)

        self.sendtodisplay(self.dynamic_image)
        self.screen.last_player_image = self.dynamic_image.copy()

    @check_perfo
    def display_menu(self, choices, marked, start, icons='nav', redraw_static=False,
                     use_last_image=False):
        if use_last_image:
            self.sendtodisplay(self.screen.last_player_image)
            return

        # Draw static elements only if needed
        if redraw_static or self.static_image is None:
            # This is the canvas on which we will draw.
            # (the current image is the default background or the album image)
            self.static_image = ImageDraw.Draw(self.screen.default_background, 'RGBA')

            # Draw first the background with static elements such as the symbols
            if icons == 'nav':
                # Fontawesome symbol ok
                self.draw_utils.draw_symbol(self.static_image, 0, 50, u"\uf14a")
                # Fontawesome symbol up
                self.draw_utils.draw_symbol(self.static_image, 210, 50, u"\uf151")
                # Fontawesome symbol back
                self.draw_utils.draw_symbol(self.static_image, 0, 170, u"\uf0e2")
                # Fontawesome symbol down
                self.draw_utils.draw_symbol(self.static_image, 210, 170, u"\uf150")
            elif icons == 'info':
                # Fontawesome symbol info
                self.draw_utils.draw_symbol(self.static_image, 10, 10, u"\uf05a")
            elif icons == 'seek':
                # Fontawesome symbol ok
                self.draw_utils.draw_symbol(self.static_image, 0, 50, u"\uf14a")
                # Fontawesome symbol forward
                self.draw_utils.draw_symbol(self.static_image, 210, 50, u"\uf04e")
                # Fontawesome symbol back
                self.draw_utils.draw_symbol(self.static_image, 0, 170, u"\uf0e2")
                # Fontawesome symbol backward
                self.draw_utils.draw_symbol(self.static_image, 210, 170, u"\uf04a")

        # Then draw the dynamic elements such as the menu content
        self.dynamic_image = self.static_image.copy()
        self.draw_utils.draw_menu_content(self.dynamic_image, choices, start, marked, self.max_list)
        self.draw_utils.draw_page_indicator(self.dynamic_image, marked, len(choices), self.max_list)

        self.sendtodisplay(self.dynamic_image)
        self.screen.last_menu_image = self.dynamic_image.copy()
