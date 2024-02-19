"""
Just a test file to check if the page is being created properly
"""

import os
import sys
from PIL import Image,ImageDraw,ImageFont 

fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'font')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

font = lambda x: ImageFont.truetype(os.path.join(fontdir, 'consola.ttf'), x)

class Page():
    def __init__(self, background_color):
        self.background_color = background_color
        self.mode = 0
        self.page_change_flag = 1
        self.image = Image.new('1', (250, 122), self.background_color)
        self.draw = ImageDraw.Draw(self.image)


    def page_4_update(self):
        """# TOP 3 PROCESSES"""
        top5 = [
            ['python3', '1.0', '22.5'],
            ['systemd', '0.1', '10.5'],
            ['bash', '0.1', '10.5'],
            ['chromium', '24.1', '2210.5'],
            ['some-quite-long-name', '20.1', '5210.5'],
        ]
        self.draw.rectangle((0, 26, 250, 250), fill = self.background_color)
        self.draw.text((60, 0), "TOP 5 PROCESSES", font = font(18), fill = 255-self.background_color)
        self.draw.line([(0,25),(250,25)], fill = 255-self.background_color,width = 2)

        self.draw.text((6, 26), "Name", font = font(14), fill = 255-self.background_color)
        self.draw.text((150, 26), "CPU", font = font(14), fill = 255-self.background_color)
        self.draw.text((190, 26), "MEM(MB)", font = font(14), fill = 255-self.background_color)
        for i in range(5):
            self.draw.text((6, 40 + 14 * i), top5[i][0][:17], font = font(14), fill = 255-self.background_color)
            self.draw.text((150, 40 + 14 * i), top5[i][1], font = font(14), fill = 255-self.background_color)
            self.draw.text((190, 40 + 14 * i), top5[i][2], font = font(14), fill = 255-self.background_color)



if __name__ == "__main__":
    p = Page(0)
    p.page_4_update()
    p.image.show()
    p.image.save("page_4.bmp")
    print("page_4.bmp saved")