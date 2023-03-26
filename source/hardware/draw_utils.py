from source.player.music import Music
from source.debug import check_perfo
from time import strftime, gmtime
from math import ceil
from PIL import Image, ImageDraw

DEFAULT_IMAGE = 'images/default.jpg'
PLAY_BUTTON_UNICODE = u"\uf04B"
PAUSE_BUTTON_UNICODE = u"\uf04C"
STOP_BUTTON_UNICODE = u"\uf04D"
MENU_BUTTON_UNICODE = u"\uf0c9"

VOLUME_LOW_UNICODE = u"\uf027"
VOLUME_HIGH_UNICODE = u"\uf028"


class ScreenData:
    def __init__(self) -> None:
        self.width = 240
        self.height = 240
        self.screen_size = (self.width, self.height)
        self.default_background = Image.open(DEFAULT_IMAGE).resize(self.screen_size)
        self.static_image = self.default_background.copy()
        self.last_player_image = self.default_background.copy()
        self.last_menu_image = self.default_background.copy()

        self.current_image = self.default_background.copy()
        self.second_image = self.default_background.copy()
        self.third_image = self.default_background.copy()
        self.image_check = ''
        self.last_refresh = 0


class OverlayData:
    def __init__(self) -> None:
        self.txt_color = (255, 255, 255)
        self.str_color = (15, 15, 15)
        self.bar_bg_color = (200, 200, 200)
        self.bar_color = (255, 255, 255)
        self.dark = False

    def update_contrast_overlay(self, im_stats):
        """ in case of dark background, change the overlay color """
        im_mean = im_stats.mean
        mn = sum(im_mean) / len(im_mean)
        self.txt_color = (255, 255, 255)
        self.str_color = (15, 15, 15)
        self.bar_bg_color = (200, 200, 200)
        self.bar_color = (255, 255, 255)
        self.dark = False
        if mn > 175:
            self.txt_color = (55, 55, 55)
            self.str_color = (200, 200, 200)  # v0.0.4 needed for shadow
            self.dark = True
            self.bar_bg_color = (255, 255, 255)
            self.bar_color = (100, 100, 100)
        if mn < 80:
            self.txt_color = (200, 200, 200)


class DrawUtils:
    def __init__(self, fonts, screen, overlay) -> None:
        self.fonts = fonts
        self.screen = screen
        self.overlay = overlay

    def draw_page_indicator(self, canvas: ImageDraw, current_page, total_pages, max_pages):
        """Draws the page indicator
        Such as 1/3, 2/3, 3/3
        on the bottom of the screen

        Args:
            current_page (_type_): Current page number
            total_pages (_type_): Total pages number
            result (_type_): _description_
        """
        # No need to draw page indicator if there is only one page
        if total_pages == 1:
            return
        page = int(ceil((current_page + 1)/total_pages))
        pages = int(ceil(max_pages/total_pages))
        pagestring = ''.join([str(page), '/', str(pages)])
        _, _, x, y = self.text_size_on_screen(pagestring, self.fonts['FONT_M'])
        self.draw_text(canvas, x, self.screen.height - y, pagestring, self.fonts['FONT_M'])

    def draw_text(self, canvas: ImageDraw, x, y, text, fontstring=None, fillstring=(255, 255, 255)):
        """draw text"""
        if not canvas:
            return
        if not text:
            return
        if fontstring is None:
            fontstring = self.fonts['FONT_M']
        canvas.text((x, y), text, font=fontstring, fill=fillstring)

    def draw_symbol(self, canvas: ImageDraw, x, y, text):
        """draw symbols"""
        self.draw_text(canvas, x, y, text)

    def draw_text_shadowed(self, canvas: ImageDraw, text, fontsize, top, shadowoffset=1):
        """draw content"""
        text_width, _, _, _ = self.text_size_on_screen(text, self.fonts['FONT_M'])
        # Get the text position from the text size on the screen
        if text_width <= self.screen.width:
            text_position_x = (self.screen.width - text_width)//2
        else:
            text_position_x = 0

        # Draw the text shadow
        self.draw_text(canvas, text_position_x + shadowoffset, top + shadowoffset,
                       text, fontsize, self.overlay.str_color)
        # Draw the text
        self.draw_text(canvas, text_position_x, top, text,
                       fontsize, self.overlay.txt_color)

    def draw_timebar(self, canvas: ImageDraw, seek, duration):
        if seek and duration and seek != 0 and duration != 0:
            # background
            canvas.rectangle((5, 230, self.screen.width - 5, 230 + 8), self.overlay.bar_bg_color)
            # bar foreground
            canvas.rectangle((5, 230, int(seek/duration/1000)*(self.screen.width-10), 230 + 8),
                             self.overlay.bar_color)

            hour = strftime("%#H", gmtime(duration - int(float(seek)/1000)))
            if hour == '0':
                remaining = ''.join(['-', strftime("%M:%S",
                                                   gmtime(duration - int(float(seek)/1000)))])
            else:
                minute = strftime("%#M", gmtime(duration - int(float(seek)/1000)))
                minute = str((int(hour)*60) + int(minute))
                remaining = ''.join(['-', minute, ':',
                                     strftime("%S", gmtime(duration - int(float(seek)/1000)))])

            text_size = self.text_size_on_screen(remaining, self.fonts['FONT_M'])
            self.draw_text(canvas, self.screen.width - text_size - 2 + 2, 206 - 2 + 2, remaining,
                           self.fonts['FONT_M'], self.overlay.str_color)  # shadow, fill by mean
            self.draw_text(canvas, self.screen.width - text_size - 2, 206 - 2, remaining,
                           self.fonts['FONT_M'], self.overlay.txt_color)  # fill by mean

    def draw_volume_overlay(self, canvas: ImageDraw, volume):
        if volume >= 0 and volume <= 49:
            self.draw_text(canvas, 200, 174, VOLUME_LOW_UNICODE,
                           self.fonts['FONT_FAS'], self.overlay.txt_color)
        else:
            self.draw_text(canvas, 200, 174, VOLUME_HIGH_UNICODE,
                           self.fonts['FONT_FAS'], self.overlay.txt_color)

        canvas.rectangle((5, 184, self.screen.width - 44, 184 + 8),
                         self.overlay.bar_bg_color)  # background

        canvas.rectangle((5, 184, 5 + int((volume/100)*(self.screen.width - 48)),
                          184 + 8), self.overlay.bar_color)  # foreground

    def draw_overlay(self, canvas: ImageDraw, player_status, music_data: Music):
        # Draw play/pause button
        if player_status in ['pause', 'stop']:
            self.draw_text(canvas, 4, 53, PLAY_BUTTON_UNICODE,
                           self.fonts['FONT_FAS'], self.overlay.txt_color)
        else:
            self.draw_text(canvas, 4, 53, PAUSE_BUTTON_UNICODE,
                           self.fonts['FONT_FAS'], self.overlay.txt_color)

        # Draw menu button
        self.draw_text(canvas, 210, 53, MENU_BUTTON_UNICODE,
                       self.fonts['FONT_FAS'], self.overlay.txt_color)

        # text
        if music_data:
            self.draw_text_shadowed(canvas, music_data.artist, self.fonts['FONT_M'], 7, 2)
            self.draw_text_shadowed(canvas, music_data.album_name, self.fonts['FONT_M'], 35, 2)
            self.draw_text_shadowed(canvas, music_data.title, self.fonts['FONT_L'], 105, 2)

    def text_size_on_screen(self, text, font):
        """helper for width and height of text"""
        bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), text, font=font)
        len1 = bbox[2] - bbox[0]
        hei1 = bbox[3] - bbox[1]

        x = (self.screen.width - len1)//2
        y = (self.screen.height - hei1)//2
        return [len1, hei1, x, y]

    @check_perfo
    def draw_menu_content(self, canvas: ImageDraw, text, start, marked, listmax1):
        if text == []:
            return
        if isinstance(text, list):  # check if text is array
            starting_position = [i // listmax1 * listmax1
                                 for i in range(0, len(text))]
            start = starting_position[marked]

            result = len(text)  # count items of list/array
            totaltextheight = 0
            i = 0
            # Loop for finding out the sum of textheight for positioning, only text to display
            listbis = start + listmax1
            if listbis > result:
                listbis = result
            for i in range(start, listbis):  # v.0.0.4 range max werteliste
                totaltextheight += self.text_size_on_screen(text[0+i], self.fonts['FONT_M'])[1]
            y = (self.screen.height // 2) - (totaltextheight // 2)  # startheight
            i = 0

            # Loop for creating text to display
            for i in range(start, listbis):  # v.0.0.4
                len1, hei1, x, _ = self.text_size_on_screen(text[0+i], self.fonts['FONT_M'])
                if x < 0:  # v.0.0.4 dont center text if to long
                    x = 0
                if i == marked:
                    canvas.rectangle((x, y + 2, x + len1, y + hei1), (255, 255, 255))
                    self.draw_text(canvas, x, y, text[0+i], self.fonts['FONT_M'], (0, 0, 0))
                else:
                    self.draw_text(canvas, x + 3, y + 3, text[0+i], self.fonts['FONT_M'],
                                   (15, 15, 15))
                    self.draw_text(canvas, x, y, text[0+i], self.fonts['FONT_M'], (255, 255, 255))
                y += hei1  # add line to startheigt for next entry
        else:
            len1, hei1, x, y = self.text_size_on_screen(text, self.fonts['FONT_M'])
            # Rectangle behind text
            canvas.rectangle((x, y, x + len1, y + hei1), (255, 255, 255))
            self.draw_text(canvas, x, y, text, self.fonts['FONT_M'], (0, 0, 0))
