import time
from math import ceil
from PIL import Image, ImageDraw

from source import SIMULATOR
from source.debug import print_debug, check_perfo

if SIMULATOR:
    import source.simulator.ST7789 as ST7789  # simulator
else:
    import ST7789


class DisplayHandler:
    def __init__(self, fonts, messages, time_to_sleep=60, max_list=5) -> None:
        self.fonts = fonts
        self.messages = messages

        # screen
        self.screen.width = 240
        self.screen.height = 240
        self.screen.screen_size = (self.width, self.height)
        self.screen.default_background = Image.open('images/default.jpg').resize(self.screen_size)
        self.screen.current_image = self.screen.default_background.copy()
        self.screen.second_image = self.screen.default_background.copy()
        self.screen.third_image = self.screen.default_background.copy()
        self.screen.image_check = None
        self.screen.last_refresh = 0
        self.screen.max_list = max_list

        # screen.sleep
        self.screen.sleep.sleeping = False
        self.screen.sleep.time_to_sleep = time_to_sleep
        self.screen.sleep.timer = time.time()

        # overlay
        self.overlay.txt_color = (255, 255, 255)
        self.overlay.str_color = (15, 15, 15)
        self.overlay.bar_bg_color = (200, 200, 200)
        self.overlay.bar_color = (255, 255, 255)
        self.overlay.dark = False

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
        self.display_stuff(self.screen.default_background)

    def display_disconnect(self):
        """display disconnect"""
        self.display.set_backlight(True)
        self.display_stuff(self.screen.default_background,
                           self.messages['LOSTCONNECTION'], 0, 0, 'info')

    def refresh(self):
        pass

    @check_perfo
    def sendtodisplay(self, image_to_display):
        """send img to display"""
        self.screen.last_refresh = time()
        self.display_stuff(image_to_display)

    @check_perfo
    def display_stuff(self, picture, text, marked, start, icons='nav'):
        """create image and overlays"""

        def f_drawtext(x, y, text, fontstring, fillstring=(255, 255, 255)):
            """draw text"""
            draw3.text((x, y), text, font=fontstring, fill=fillstring)

        def f_drawsymbol(x, y, text, fontstring=self.fonts['FONT_FAS'], fillstring=(255, 255, 255)):
            """draw symbols"""
            draw3.text((x, y), text, font=fontstring, fill=fillstring)

        @check_perfo
        def f_textcontent(text, start, listmax1):
            """draw content"""
            if isinstance(text, list):  # check if text is array
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

        @check_perfo
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
            f_drawsymbol(210, 50, u"\uf04e")  # Fontawesome symbol forward
            f_drawsymbol(0, 170, u"\uf0e2")  # Fontawesome symbol back
            f_drawsymbol(210, 170, u"\uf04a")  # Fontawesome symbol backward

        f_page(marked, self.screen.max_list, result)

        self.sendtodisplay(self.screen.third_image)
        return self.screen.third_image
