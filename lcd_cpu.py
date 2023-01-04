"""
Using I2C LCD 2*16 to show information
Initially for the Orange Pi 5
RC 2023-01-04

2023-01-04 v0.1.0: let's start
"""

import sys
import os
import argparse
from datetime import datetime
from datetime import timedelta
from time import sleep
from time import time
from time import strftime
from time import gmtime
from typing import ChainMap

import socket
import platform
import unicodedata
import psutil

class LCD16CPU:
    """
    This is the class to manage the LCD 16x2 
    """
    def __init__(self): 
        
        self.__version__ = "v0.1.0"
                
        description = "LCD16CPU Monitor you Pi with a 16x2 LCD"
        
        lcd_help = "LCD address something like 0x3f"
        i2c_help = "i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2 or OPi5"
        virtual_lcd_help = "yes or no, yes means no LCD, just print on screen"
        display_mode_help = "set cpu or cpuram or cpudisk or clock"
        
        parser = argparse.ArgumentParser(description = description)
        parser.add_argument("-l","--lcd", type=lambda x: int(x, 0), default=0x3f, help = lcd_help)
        parser.add_argument("-i","--i2c_port", type=int, default=1, help = i2c_help)
        parser.add_argument("-v","--virtual_lcd", type=str, default="yes", help = virtual_lcd_help)
        parser.add_argument("-d","--display_mode", type=str, default="", help = display_mode_help)

        
        try:
            args = parser.parse_args()
        except Exception as e:
            print("Error: " + str(e))
            sys.exit(1)

        if os.getenv('LMS_LCD') is not None:
            args.player_name = os.environ['LMS_LCD']
        if os.getenv('LMS_I2C_PORT') is not None:
            args.i2c_port = os.environ['LMS_I2C_PORT']
        if os.getenv('LMS_VIRTUAL_LCD') is not None:
            args.virtual_lcd = os.environ['LMS_VIRTUAL_LCD']
        if os.getenv('LMS_DISPLAY_MODE') is not None:
            args.display_mode = os.environ['LMS_DISPLAY_MODE'] 
        
        self.display_mode = args.display_mode
        lcd = args.lcd
        i2c_port  = args.i2c_port
        virtual_lcd = args.virtual_lcd
        self.display_mode = args.display_mode

        print("-------------------------------")
        print("LCD16CPU class " + self.__version__ + " started!")
        print("params are")
        print("lcd address : " + str(lcd))
        print("i2c_port    : " + str(i2c_port))
        print("virtual_lcd : " + virtual_lcd)
        print("display_mode: " + self.display_mode)
        print("-------------------------------")



        if "Windows" in platform.platform() or virtual_lcd == "yes":
            import no_lcddriver
            self.lcd = no_lcddriver.lcd(address = lcd, columns=16) 
        else:
            import lcddriver
            self.lcd = lcddriver.lcd(address = lcd, columns=16, i2c_port=i2c_port)
            self.lcd.lcd_clear()
            self.lcd.lcd_display_string("      C&R ID ", 1)
            self.lcd.lcd_display_string("    Audiofolies" , 2)
            sleep(2)

    

    def cpu_usage(self):
        """
        Print the 2 CPU usage lines
        """
        try:
            self.lcd.lcd_display_string("CPU : " + str(psutil.cpu_percent()) +"% t:" +  
                str(int(psutil.sensors_temperatures()["soc_thermal"][0][1])), 1)
        except:
            self.lcd.lcd_display_string("CPU : " + str(psutil.cpu_percent()) +"% t:?", 1)
        
        self.lcd.lcd_display_string("freq: " + str(int(psutil.cpu_freq().current)), 2)

    def cpu_ram(self):
        """
        Print the 2 RAM usage lines
        """
        self.lcd.lcd_display_string("RAM : " + str(int(psutil.virtual_memory().total /1024 / 1024)) +"Mo ", 1)
        # print("total " + str(psutil.virtual_memory().total / 1024 / 1024))
        # print("avail " + str(psutil.virtual_memory().available / 1024 / 1024))
        total = psutil.virtual_memory().total / 1024 / 1024
        avail = psutil.virtual_memory().available / 1024 / 1024
        pct = (total - avail) / total * 100
        # print("pct " + str(round(pct,1)))
        self.lcd.lcd_display_string("use " + str(int(psutil.virtual_memory().used / 1024 / 1024)) 
        + "Mo " + str(round(pct,1)) + "%" , 2)

    def cpu_disk(self):
        """
        Print disks info
        """
        hdd = psutil.disk_partitions()
        data = []
        nbdisk = 0
        for partition in hdd:
            device = partition.device
            path = partition.mountpoint
            fstype = partition.fstype

            drive = psutil.disk_usage(path)
            total = drive.total
            total = total / 1000000000
            if total > 1:
                nbdisk = nbdisk + 1
                used = drive.used
                used = used / 1000000000
                free = drive.free
                free = free / 1000000000
                percent = int(drive.percent)
                drives = {
                    "device": device,
                    "path": path,
                    "fstype": fstype,
                    "total": float("{0: .2f}".format(total)),
                    "used": float("{0: .2f}".format(used)),
                    "free": float("{0: .2f}".format(free)),
                    "percent": percent
                }
                
                self.lcd.lcd_display_string("Disk " + str(nbdisk) + ": " + str(int(total)) + "G", 1)
                self.lcd.lcd_display_string("part: " + device, 2)
                sleep(2)
                self.lcd.lcd_display_string("used: " + str(int(used )) + "G*" + str(percent) + "%", 2)
                sleep(5)


    def clock(self):
        today = datetime.today()
        self.lcd.lcd_display_string(today.strftime("Clock %d/%m/%Y"), 1)
        self.lcd.lcd_display_string(today.strftime("Time  %H:%M:%S"), 2)
        sleep(.8)
    
    def main_loop(self):
        while True:
            if "cpu" in self.display_mode:
                if self.display_mode == "cpuonly":
                    self.cpu_usage()
                elif self.display_mode == "cpuram":
                    self.cpu_ram()
                elif self.display_mode == "cpudisk":
                    self.cpu_disk()
                else:
                    self.cpu_usage()
                    sleep(3)
                    self.cpu_ram()
                    sleep(3)
                    self.cpu_disk()

                sleep(.8)
            else:
                self.clock()
                sleep(.8)

if __name__ == "__main__":
        
    myLcd = LCD16CPU()
    myLcd.main_loop()


