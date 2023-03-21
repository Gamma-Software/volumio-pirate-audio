from time import strftime, gmtime, time  # v.0.0.7
from math import ceil
from numpy import mean
from PIL import Image, ImageDraw, ImageStat, ImageFilter

from source import SIMULATOR
from source.debug import check_perfo

if SIMULATOR:
    import source.simulator.ST7789 as ST7789  # simulator
else:
    import ST7789

DEFAULT_IMAGE = 'images/default.jpg'
PLAY_BUTTON_UNICODE = u"\uf04B"
PAUSE_BUTTON_UNICODE = u"\uf04C"
STOP_BUTTON_UNICODE = u"\uf04D"
MENU_BUTTON_UNICODE = u"\uf0c9"

#VOLUME_MUTE_UNICODE = u"\uf2e2"
VOLUME_LOW_UNICODE = u"\uf027"
#VOLUME_UNICODE = u"\uf6a8"
VOLUME_HIGH_UNICODE = u"\uf028"


class ScreenSleepData:
    def __init__(self, time_to_sleep) -> None:
        self.sleeping = False
        self.time_to_sleep = time_to_sleep
        self.timer = time()


class ScreenData:
    def __init__(self, max_list, time_to_sleep) -> None:
        self.width = 240
        self.height = 240
        self.screen_size = (self.width, self.height)
        self.default_background = Image.open(DEFAULT_IMAGE).resize(self.screen_size)
        self.current_image = self.default_background.copy()
        self.second_image = self.default_background.copy()
        self.third_image = self.default_background.copy()
        self.image_check = ''
        self.last_refresh = 0
        self.max_list = max_list
        self.sleep = ScreenSleepData(time_to_sleep)


class OverlayData:
    def __init__(self) -> None:
        self.txt_color = (255, 255, 255)
        self.str_color = (15, 15, 15)
        self.bar_bg_color = (200, 200, 200)
        self.bar_color = (255, 255, 255)
        self.dark = False

    def contrast_overlay(self, im_stats):
        """ in case of dark background, change the overlay color """
        im_mean = im_stats.mean
        mn = mean(im_mean)
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


class DisplayHandler:
    def __init__(self, fonts, messages, time_to_sleep=60, max_list=5) -> None:
        self.fonts = fonts
        self.messages = messages

        # screen
        self.screen = ScreenData(max_list, time_to_sleep)

        # overlay
        self.overlay = OverlayData()

        self.display = ST7789.ST7789(
            height=240,  # v0.0.6
            width=240,  # v0.0.6
            rotation=90,  # Needed to display the right way up on Pirate Audio
            port=0,       # SPI port
            cs=1,         # SPI port Chip-select channel
            dc=9,         # BCM pin used for data/command
            backlight=13,
            spi_speed_hz=80 * 1000 * 1000,
            offset_left=0,  # v0.0.6
            offset_top=0  # v0.0.6
        )

    def clean(self):
        pass

    def display_connect(self):
        """display connect"""
        self.display.set_backlight(True)
        self.display_stuff(self.screen.default_background,
                           self.messages['DISPLAY']['WAIT'], 0, 0, 'info')

    def display_disconnect(self):
        """display disconnect"""
        self.display.set_backlight(True)
        self.display_stuff(self.screen.default_background,
                           self.messages["DISPLAY"]['LOSTCONNECTION'], 0, 0, 'info')

    def display_menu(self, menu_list, cursor, icon='nav'):
        """display menu"""
        self.display.set_backlight(True)

        if len(menu_list) == 0:
            menu_list = self.messages['DISPLAY']['EMPTY']
        self.display_stuff(self.screen.default_background,
                           menu_list, cursor, cursor, icon)

    def display_shutdown(self):
        self.display.set_backlight(True)
        # TODO : add a shutdown message
        self.display_stuff(self.screen.default_background,
                           ['executing:', 'shutdown'], 0, 0, 'info')

    def display_reboot(self):
        self.display.set_backlight(True)
        # TODO : add a reboot message
        self.display_stuff(self.screen.default_background,
                           ['executing:', 'reboot'], 0, 0, 'info')

    def refresh(self):
        pass

    #@check_perfo
    def sendtodisplay(self, image_to_display):
        """send img to display"""
        self.screen.last_refresh = time()
        self.display.display(image_to_display)

    #@check_perfo
    def display_stuff(self, picture, text, marked, start, icons='nav'):
        """create image and overlays"""

        def f_drawtext(x, y, text, fontstring, fillstring=(255, 255, 255)):
            """draw text"""
            draw3.text((x, y), text, font=fontstring, fill=fillstring)

        def f_drawsymbol(x, y, text, fontstring=self.fonts['FONT_FAS'], fillstring=(255, 255, 255)):
            """draw symbols"""
            draw3.text((x, y), text, font=fontstring, fill=fillstring)

        #@check_perfo
        def f_textcontent(text, start, listmax1):
            if text == []:
                return
            """draw content"""
            if isinstance(text, list):  # check if text is array
                starting_position = [i // self.screen.max_list * self.screen.max_list
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
                    totaltextheight += f_xy(text[0+i], self.fonts['FONT_M'])[1]
                Y = (self.screen.height // 2) - (totaltextheight // 2)  # startheight
                i = 0

                # Loop for creating text to display
                for i in range(start, listbis):  # v.0.0.4
                    XY = f_xy(text[0+i], self.fonts['FONT_M'])
                    hei1 = XY[1]
                    X2 = XY[2]
                    if X2 < 0:  # v.0.0.4 dont center text if to long
                        X2 = 0
                    if i == marked:
                        draw3.rectangle((X2, Y + 2, X2 + XY[0], Y + hei1), (255, 255, 255))
                        f_drawtext(X2, Y, text[0+i], self.fonts['FONT_M'], (0, 0, 0))
                    else:
                        f_drawtext(X2 + 3, Y + 3, text[0+i], self.fonts['FONT_M'], (15, 15, 15))
                        f_drawtext(X2, Y, text[0+i], self.fonts['FONT_M'])
                    Y += hei1  # add line to startheigt for next entry
            else:
                result = 1  # needed for right pageindex
                XY = f_xy(text, self.fonts['FONT_M'])
                len1 = XY[0]
                hei1 = XY[1]
                X2 = XY[2]
                y2 = XY[3]
                draw3.rectangle((X2, y2, X2 + len1, y2 + hei1), (255, 255, 255))
                f_drawtext(X2, y2, text, self.fonts['FONT_M'], (0, 0, 0))
            return result

        def f_xy(text, font):
            """helper for width and height of text"""
            if SIMULATOR:
                bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), text, font=font)
                len1 = bbox[2] - bbox[0]
                hei1 = bbox[3] - bbox[1]
            else:
                len1, hei1 = draw3.textsize(text, font)

            x = (self.screen.width - len1)//2
            Y = (self.screen.height - hei1)//2
            return [len1, hei1, x, Y]

        #@check_perfo
        def f_page(marked, listmax2, result):
            """pageindicator"""
            page = int(ceil((float(marked) + 1)/float(listmax2)))
            pages = int(ceil(float(result)/float(listmax2)))
            if pages != 1:  # only show index if more than one site
                pagestring = ''.join([str(page), '/', str(pages)])
                XY = f_xy(pagestring, self.fonts['FONT_M'])
                f_drawtext(XY[2], self.screen.height - XY[1], pagestring, self.fonts['FONT_M'])

        if picture == self.screen.default_background:
            self.screen.third_image = self.screen.default_background.copy()
        else:
            self.screen.third_image = Image.open(picture).convert('RGBA')  # v.0.0.4
        draw3 = ImageDraw.Draw(self.screen.third_image, 'RGBA')
        result = f_textcontent(text, start, self.screen.max_list)
        # draw symbols
        if icons == 'nav':
            f_drawsymbol(0, 50, u"\uf14a")  # Fontawesome symbol ok
            f_drawsymbol(210, 50, u"\uf151")  # Fontawesome symbol up
            f_drawsymbol(0, 170, u"\uf0e2")  # Fontawesome symbol back
            f_drawsymbol(210, 170, u"\uf150")  # Fontawesome symbol down
        elif icons == 'info':
            f_drawsymbol(10, 10, u"\uf05a")  # Fontawesome symbol info
        elif icons == 'seek':
            f_drawsymbol(0, 50, u"\uf14a")  # Fontawesome symbol ok
            f_drawsymbol(210, 50, u"\uf04e")  # Fontawesome symbol forward
            f_drawsymbol(0, 170, u"\uf0e2")  # Fontawesome symbol back
            f_drawsymbol(210, 170, u"\uf04a")  # Fontawesome symbol backward

        f_page(marked, self.screen.max_list, result)

        self.sendtodisplay(self.screen.third_image)
        return self.screen.third_image

    def f_textsize(self, text, font, fontsize):
        """"helper textsize"""
        if not self.draw:
            raise RuntimeError('No draw object available')

        if SIMULATOR:
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), text, font=font)
            w1 = bbox[2] - bbox[0]
        else:
            w1, _ = self.draw.textsize(text, fontsize)
        return w1

    def f_drawtext(self, x, y, text, fontstring, fillstring):
        """draw text"""
        if not self.draw:
            raise RuntimeError('No draw object available')

        self.draw.text((x, y), text, font=fontstring, fill=fillstring)

    def f_x1(self, textwidth):
        """helper textwidth"""
        if textwidth <= self.screen.width:
            x1 = (self.screen.width - textwidth)//2
        else:
            x1 = 0
        return x1

    def f_content(self, text, fontsize, top, shadowoffset=1):
        """draw content"""
        w1 = self.f_textsize(text, self.fonts['FONT_M'], fontsize)
        x1 = self.f_x1(w1)
        self.f_drawtext(x1 + shadowoffset, top + shadowoffset,
                        text, fontsize,
                        self.overlay.str_color)
        self.f_drawtext(x1, top, text,
                        fontsize, self.overlay.txt_color)

    def f_background(self, album_image):
        """helper background"""
        try:  # to catch not displayable images
            self.screen.current_image = Image.open(album_image).convert('RGBA')  # v.0.04 gab bei spotify probleme
            self.screen.current_image = self.screen.current_image.resize(self.screen.screen_size)
            self.screen.current_image = self.screen.current_image.filter(ImageFilter.BLUR)  # Blur
        except (ValueError, RuntimeError):
            self.screen.current_image = self.screen.default_background.copy()

        self.screen.second_image = self.screen.current_image.copy()

        im_stat = ImageStat.Stat(self.screen.current_image)
        self.overlay.contrast_overlay(im_stat)
        return self.screen.current_image

    def f_displayoverlay(self, varstatus, volume, data):
        """displayoverlay"""
        self.draw = ImageDraw.Draw(self.screen.current_image, 'RGBA')

        if varstatus in ['pause', 'stop']:
            self.f_drawtext(4, 53, PLAY_BUTTON_UNICODE,
                            self.fonts['FONT_FAS'], self.overlay.txt_color)
        else:
            self.f_drawtext(4, 53, PAUSE_BUTTON_UNICODE,
                            self.fonts['FONT_FAS'], self.overlay.txt_color)
        self.f_drawtext(210, 53, MENU_BUTTON_UNICODE,
                        self.fonts['FONT_FAS'], self.overlay.txt_color)

        if volume >= 0 and volume <= 49:
            self.f_drawtext(200, 174, VOLUME_LOW_UNICODE,
                            self.fonts['FONT_FAS'], self.overlay.txt_color)
        else:
            self.f_drawtext(200, 174, VOLUME_HIGH_UNICODE,
                            self.fonts['FONT_FAS'], self.overlay.txt_color)

        # text
        if 'artist' in data.keys():
            if data['artist']:
                self.f_content(data['artist'], self.fonts['FONT_M'], 7, 2)
        if 'album' in data.keys():
            if data['album']:
                self.f_content(data['album'], self.fonts['FONT_M'], 35, 2)
        if 'title' in data.keys():
            if data['title']:
                self.f_content(data['title'], self.fonts['FONT_L'], 105, 2)

        # volumebar
        self.draw.rectangle((5, 184, self.screen.width - 44, 184 + 8),
                            self.overlay.bar_bg_color)  # background

        self.draw.rectangle((5, 184, 5 + int((float(volume)/100)*(self.screen.width - 48)),
                            184 + 8), self.overlay.bar_color)  # foreground

    def f_timebar(self, data, duration):
        """helper timebar"""
        self.draw = ImageDraw.Draw(self.screen.current_image, 'RGBA')
        if 'seek' in data and 'duration' in data and data['seek'] is not None and data['seek'] != 0 and data['duration'] != 0:
            self.draw.rectangle((5, 230, self.screen.width - 5, 230 + 8), self.overlay.bar_bg_color)  # background
            self.draw.rectangle((5, 230, int((float(int(float(data['seek'])/1000))/float(int(float(data['duration']))))*(self.screen.width-10)), 230 + 8), self.overlay.bar_color)

            hour = strftime("%#H", gmtime(duration - int(float(data['seek'])/1000)))
            if hour == '0':
                remaining = ''.join(['-', strftime("%M:%S", gmtime(duration - int(float(data['seek'])/1000)))])
            else:
                minute = strftime("%#M", gmtime(duration - int(float(data['seek'])/1000)))
                minute = str((int(hour)*60) + int(minute))
                remaining = ''.join(['-', minute, ':', strftime("%S", gmtime(duration - int(float(data['seek'])/1000)))])
            # print('remaining:', remaining)

            #remaining = ''.join(['-', strftime("%M:%S", gmtime(DURATION - int(float(SEEK)/1000)))])
            w4 = self.f_textsize(remaining, self.fonts['FONT_M'], self.fonts['FONT_M'])
            self.f_drawtext(self.screen.width - w4 - 2 + 2, 206 - 2 + 2, remaining, self.fonts['FONT_M'], self.overlay.str_color)  # shadow, fill by mean
            self.f_drawtext(self.screen.width - w4 - 2, 206 - 2, remaining, self.fonts['FONT_M'], self.overlay.txt_color)  # fill by mean
