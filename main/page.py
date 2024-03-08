import sys
import os
import logging
import time

from PIL import Image,ImageDraw,ImageFont

from utils import *

logger = logging.getLogger(__name__)

fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'font')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from epd_lib import epd2in13_V2 

epd = epd2in13_V2.EPD()

# font8 = ImageFont.truetype(os.path.join(fontdir, 'consola.ttf'), 8) 
# font14 = ImageFont.truetype(os.path.join(fontdir, 'consola.ttf'), 14)
# font16 = ImageFont.truetype(os.path.join(fontdir, 'consola.ttf'), 16)
# font18 = ImageFont.truetype(os.path.join(fontdir, 'consola.ttf'), 18)
# font21 = ImageFont.truetype(os.path.join(fontdir, 'consola.ttf'), 21)
# font24 = ImageFont.truetype(os.path.join(fontdir, 'consola.ttf'), 24)

font = lambda x: ImageFont.truetype(os.path.join(fontdir, 'consola.ttf'), x)

#Page class
class Page():
    """
    Page 1: Basic Info
    Page 2: Status
    Page 3: Disk Info
    Page 4: Top 5 Processes
    """
    def __init__(self, background_color):
        self.background_color = background_color
        self.mode = 0
        self.page_change_flag = 1
        self.image = Image.new('1', (epd.height, epd.width), self.background_color)
        self.draw = ImageDraw.Draw(self.image)
        self.refresh_num = 0
        self.clear_count = 0
        self.clear_max = 5
        self.timer = 1
        # epd.init(epd.FULL_UPDATE)
        # epd.displayPartBaseImage(epd.getbuffer(self.image))
        epd.init(epd.PART_UPDATE)
    
    def clear(self):
        logging.debug("Run clear")
        self.clear_count = 0
        epd.Clear(self.background_color)
        # epd.init(epd.PART_UPDATE)

    def reset(self):
        self.clear()
        epd.init(epd.FULL_UPDATE)
        epd.display([self.background_color]*epd.width*epd.height)
        epd.init(epd.PART_UPDATE)
    
    def update(self):
        epd.displayPartial(epd.getbuffer(self.image))

    def __call__(self, p):
        self.refresh_num = 0
        
        self.image = Image.new('1', (epd.height, epd.width), self.background_color)
        self.draw = ImageDraw.Draw(self.image)
        self.clear()
        self.reset()

        eval("self.page_%s_setup()"%p)
        epd.displayPartial(epd.getbuffer(self.image))
        self.page_change_flag = 1

        while self.page_change_flag:
            t = time.time()
            cmd = "self.page_%s_update()"%p
            logging.debug(cmd)
            eval(cmd)
            # if self.clear_count > self.clear_max:
            #     print("begin")
            #     self.reset()
            self.update()

            self.refresh_num += 1
            self.clear_count += 1
            if self.refresh_num == 5 and self.mode == 0:

                self.draw.ellipse((2,2,19,19),fill = 255-self.background_color)
                self.draw.text((6, 1), 'S', font = font(16), fill = self.background_color)
                self.update()
                break
            while self.page_change_flag and time.time()-t < self.timer:
                time.sleep(0.5)
        if self.mode == 1:
            self.change_val(1)

    def page_1_setup(self):
        self.draw.text((80, 0), "BASIC INFO", font = font(18), fill = 255 - self.background_color)
        self.draw.line([(0,22),(250,22)], fill = 255 - self.background_color,width = 2)

    def page_1_update(self):
        """BASIC INFO"""
        self.draw.rectangle((37, 53, 105, 73), fill = self.background_color)

        ip_info = getIP()
        if not ip_info:
            ip_info_str = "Unknown"
            fill_len = int(14.5*len(ip_info_str))
        else:
            ip_info_str = str(ip_info)
            fill_len = int(12.5*len(ip_info_str))

        self.draw.rectangle((0, 24, fill_len, 47), fill = 255-self.background_color)
        self.draw.text((0, 26), 'IP: ' + ip_info_str, font = font(16), fill = self.background_color)

        try:
            pi_msg = pi_read()
        except Exception as e:
            logger.error("Failed to get info: %s", e)
            self.draw.text((0, 26), 'Error: Failed to get info', font = font(14), fill = 255-self.background_color)
            return

        self.draw.text((0, 53), 'CPU: ' + pi_msg['cpu_usage'] + '%', font = font(16), fill = 255-self.background_color)
        self.draw.rectangle((0, 75, 234, 85), outline = 255-self.background_color)
        self.draw.rectangle((0, 75, 234 * float(pi_msg['cpu_usage'])/100, 85), fill = 255-self.background_color)

        ram_usage = round(pi_msg['ram'][1] / pi_msg['ram'][0],2)
        self.draw.rectangle((37, 88, 105, 108), fill = self.background_color)
        self.draw.rectangle((175, 88, 235, 108), fill = self.background_color)
        self.draw.text((0, 88), 'RAM: ' + str(ram_usage) + '%', font = font(16), fill = 255-self.background_color)
        self.draw.text((120, 88), 'total: ' + str(pi_msg['ram'][0]) + 'M', font = font(16), fill = 255-self.background_color)
        self.draw.rectangle((0, 110, 234, 120), outline = 255-self.background_color)
        self.draw.rectangle((0, 110, 234 * ram_usage/100, 120), fill = 255-self.background_color) 

    def page_2_setup(self):
        self.draw.text((65, 0), "STATUS", font = font(18), fill = 255-self.background_color)
        self.draw.line([(0,25),(250,25)], fill = 255-self.background_color,width = 2)
        self.draw.text((9, 48), 'CPU', font = font(18), fill = 255-self.background_color)
        self.draw.text((100, 48), 'GPU', font = font(18), fill = 255-self.background_color)
        self.draw.text((193, 48), 'FAN', font = font(18), fill = 255-self.background_color)
        
    def page_2_update(self):
        """STATUS"""
        try:
            pi_msg = temperature_read()
            temp_cpu_text = pi_msg['cpu_temperature'] + 'C'
            temp_gpu_text = pi_msg['gpu_temperature'] + 'C'
        except Exception as e:
            logger.error("Failed to get temperature: %s", e)
            temp_cpu_text = "N/A"
            temp_gpu_text = "N/A"

        # Temp CPU icon
        self.draw.arc((8,73,16,81),180,360, fill = 255-self.background_color)
        self.draw.line([(8,77),(8,93)], fill = 255-self.background_color,width = 1)
        self.draw.line([(16,77),(16,93)], fill = 255-self.background_color,width = 1)
        self.draw.arc((2,93,22,112),-60,247, fill = 255-self.background_color)

        self.draw.ellipse((8,97,16,105),fill = 255-self.background_color)
        self.draw.line([(12.5,81),(12.5,100)], fill = 255-self.background_color,width = 1) 

        # Temp GPU icon
        self.draw.arc((95,73,103,81),180,360, fill = 255-self.background_color)
        self.draw.line([(95,77),(95,93)], fill = 255-self.background_color,width = 1)
        self.draw.line([(103,77),(103,93)], fill = 255-self.background_color,width = 1)
        self.draw.arc((89,93,109,112),-60,247, fill =255- self.background_color)

        self.draw.ellipse((95,97,103,105),fill = 255-self.background_color)
        self.draw.line([(99,81),(99,100)], fill = 255-self.background_color,width = 1)

        # Temp text
        self.draw.rectangle((23, 75, 65, 96), fill = self.background_color)
        self.draw.rectangle((110, 75, 150, 100), fill = self.background_color)

        self.draw.text((24, 75), temp_cpu_text, font = font(15), fill = 255-self.background_color)
        self.draw.text((111, 75), temp_gpu_text, font = font(15), fill = 255-self.background_color)

        # Fan icon with animation
        self.draw.ellipse((170,74,202,106),fill = 255-self.background_color)
        self.draw.pieslice((174,78,198,102),0+self.refresh_num*60,60+self.refresh_num*60, fill = self.background_color)
        self.draw.pieslice((174,78,198,102),120+self.refresh_num*60,180+self.refresh_num*60, fill = self.background_color)
        self.draw.pieslice((174,78,198,102),240+self.refresh_num*60,300+self.refresh_num*60, fill = self.background_color)
        self.draw.ellipse((182,86,190,94),fill = 255-self.background_color)
        self.draw.ellipse((184,88,188,92),fill = self.background_color)

        # Fan text
        self.draw.rectangle((206, 75, 250, 100), fill = self.background_color)
        self.draw.text((207, 75), str(fan_power_read()) + '%', font = font(15), fill = 255-self.background_color)


    def page_3_setup(self):
        self.draw.rectangle((0, 26, 250, 250), fill = self.background_color)
        self.draw.text((80, 0), "DISK INFO", font = font(18), fill = 255-self.background_color)
        self.draw.line([(0,25),(250,25)], fill = 255-self.background_color,width = 2)
    
    def page_3_update(self):
        """DISK INFO"""
        def p(a):
            a = float(a)
            if a > 1000000000:
                a = "%.3gT" % (a/1000000000)
            elif a > 1000000:
                a = "%.3gG" % (a/1000000)
            elif a > 1000:
                a = "%.3gM" % (a/1000)
            elif a > 1:
                a = "%.3gK" % a
            return a
        
        d_space = disk_space()
        self.draw.text((6, 26), 'root: ' + d_space[3], font = font(14), fill = 255-self.background_color)
        self.draw.text((102, 26), 'Size: %s / %s' % (d_space[1],d_space[0]), font = font(14), fill = 255-self.background_color)
        self.draw.rectangle((2, 43, 234, 53), outline = 255-self.background_color)
        self.draw.rectangle((3, 43, 234 * float(d_space[3].replace('%', ''))/100, 53), fill = 255-self.background_color)

        hard_disk_list = []
        try:
            hard_disk_list = portable_hard_disk_info()
        except Exception as e:
            logger.error("Failed to get disk info: %s", e)
            self.draw.text((6, 26), 'Error: Failed to get disk info', font = font(14), fill = 255-self.background_color)
            return
        
        if len(hard_disk_list) != 0 and len(hard_disk_list) < 3:
            for i in range(len(hard_disk_list)):
                self.draw.text((6, 55 + i*29), hard_disk_list[i][0][-4:].upper() +': ' + hard_disk_list[i][4], font = font(14), fill = 255-self.background_color)
                used = eval(hard_disk_list[i][2].replace('K', '').replace('M', '*1000').replace('G', '*1000000').replace('T', '*1000000000'))
                free = eval(hard_disk_list[i][3].replace('K', '').replace('M', '*1000').replace('G', '*1000000').replace('T', '*1000000000'))

                total = p(used + free)
                used = p(used)
                self.draw.text((102, 55 + i*29), "Size: %s / %s"%(used, total), font = font(14), fill = 255-self.background_color)
                self.draw.rectangle((2, 72 + i*29, 234, 82 + i*29), outline = 255-self.background_color)
                self.draw.rectangle((3, 72 + i*29, 234 * float(hard_disk_list[i][4].replace('%', ''))/100, 82 + i*29), fill = 255-self.background_color)


    def page_4_setup(self):
        self.draw.text((60, 0), "TOP 5 PROCESSES", font = font(18), fill = 255-self.background_color)
        self.draw.line([(0,25),(250,25)], fill = 255-self.background_color,width = 2)
        
    def page_4_update(self):
        """TOP 5 PROCESSES"""
        self.draw.rectangle((0, 26, 250, 250), fill = self.background_color)
        try:
            top = top_process(5)
        except Exception as e:
            logger.error("Failed to get top processes: %s", e)
            self.draw.text((6, 26), 'Error: Failed to get top processes', font = font(14), fill = 255-self.background_color)
            return
        
        self.draw.text((6, 26), "Name", font = font(14), fill = 255-self.background_color)
        self.draw.text((150, 26), "CPU", font = font(14), fill = 255-self.background_color)
        self.draw.text((190, 26), "MEM(MB)", font = font(14), fill = 255-self.background_color)
        for i in range(len(top)):
            self.draw.text((6, 40 + 14 * i), top[i][0][:17], font = font(14), fill = 255-self.background_color)
            self.draw.text((150, 40 + 14 * i), top[i][1], font = font(14), fill = 255-self.background_color)
            self.draw.text((190, 40 + 14 * i), top[i][2], font = font(14), fill = 255-self.background_color)


    def shutdown_Animation(self):
        # self.image = Image.new('1', (epd.height, epd.width), self.background_color)
        # self.draw = ImageDraw.Draw(self.image)
        
        self.reset()
        
        # self.draw.rectangle((0, 0, 250, 250), fill = 255) 
        # epd.displayPartial(epd.getbuffer(self.image))
        
        for i in range(6):
            wod = i*76
            self.draw.rectangle((0, 0, 250, 250), fill = 255)
            self.draw.rectangle((wod, 25, 135+wod, 95), outline = 0) 
            self.draw.polygon([(135+wod,25),(135+wod,95),(175+wod,60)],fill = 0)

            self.draw.polygon([(wod,25),(wod,45+i*5),(wod-15-i*10,36-i*12)],fill = 0)
            self.draw.polygon([(wod,48-i*4),(wod,71+i*4),(wod-20-i*20,60)],fill = 0)
            self.draw.polygon([(wod,71-i*5),(wod,95),(wod-15-i*10,83+i*12)],fill = 0)
            self.draw.text((5+wod, 35), 'Goodbye! Sir', font = font(18), fill = 0)
            self.draw.text((5+wod, 65), 'Sunfounder', font = font(18), fill = 0)
            epd.displayPartial(epd.getbuffer(self.image))
            time.sleep(0.5)
        
        self.draw.rectangle((0, 0, 250, 250), fill = 255)
        epd.init(epd.FULL_UPDATE)
        epd.display(epd.getbuffer(self.image))
        epd.sleep()

    def screen_sleep(self):
        epd.sleep()
        logger.info("Screen is in sleep mode")

    def screen_wake(self):
        epd.init(epd.PART_UPDATE)
        logger.info("Screen is awake")


    def change_val(self, x = 0):
        # global page_change_flag
        self.page_change_flag = x