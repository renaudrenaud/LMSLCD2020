"""
Using I2C LCD 2*16 to show information 
Specifically for the SERVER 
- it shows the IP adress
- the mount point and if something is here
- players IP adresses

2022-07-26 v1.2.0: code now manages when booting and ip = 0.0.0.0  
2022-07-26 v1.1.0: code now manages when no player
2021-12-26 v1.0.0: first lines
"""

import argparse
from datetime import datetime
from datetime import timedelta
from time import sleep
from time import time
from time import strftime
from time import gmtime
from typing import ChainMap
from lmsmanager import LmsServer
import socket
import platform
import unicodedata

class LCD16:
    """
    This is the class to manage the LCD 16x2 
    """
    def __init__(self, 
                 server:str,
                 lcd: int,
                 i2c_port: int,
                 virtual_lcd: str,
                 display_mode: str,
                 player_name:str):
    
        self.__version__ = "v1.0.0"
        
        self.player_name = player_name
        self.display_mode = display_mode
        self.local_IP = self.get_my_ip()

        self.my_server = LmsServer(server)
        # self.server_status = self.my_server.server_status()

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
            
        self.screen_lms_info()
        sleep(3)

    def get_players_info(self, playername:str="")->dict: 
        """
        Grab the information for 
        - player_name if specified
        - otherwise the first player playing music

        input
        : playername, str ie "" or "SABAJ D5"

        returns
        : dict, dicts: Player, LMS Players
        """
        
        try:
            players = self.my_server.cls_players_list()
            if players == []:
                # players List is empty
                print("zero player found!")
            else:
                for player in players:
                    if playername == player['name']:
                        return player, players
                    elif player["isplaying"] == 1 and playername == "":
                        return player, players
        except Exception  as err:
            print("Error in players detection:")
            print(err)
            return None, None 
        
        return None, players

    def get_from_loop(self, source_list, key_to_find)->str:
        """
        iterate the list and return the value when the key_to_find is found

        Parameters:
            source_list (list of dict): each element conatins a key and a value
            key_to_find (str): the key to find in the list

        returns:
        ret: str, the value found or ""

        """
        ret = ""
        for elt in source_list:
            if key_to_find in elt.keys():
                ret = elt[key_to_find]
                break

        return ret

    def get_my_ip(self)-> str:
        """
        Find my IP address
        ret: str, the ip address like 192.168.1.51
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as err:
            print("Error in get_my_ip:")
            print(err)
            return "0.0.0.0"
    
    
    def screen_lms_info(self):
        """
        Print some info on the LCD 
        - if LMS found, version, players count...
        - otherwise "LMS Not found"

        input
        : None

        returns
        : None

        """

        server = self.my_server.cls_server_status() 
        if type(server) is not dict:
            self.lcd.lcd_display_string("LMS not found", 3)
            self.lcd.lcd_display_string("no player.",4)
        else:
            res = server["result"]
            self.lcd.lcd_display_string("LMS    : v" + res["version"],1)
            self.lcd.lcd_display_string("Players: " + str(res["player count"]), 2)

    def main_loop(self):
        last_song = {}
        album = ""
        runner = "+"
        decal = 0
        song_info = None
        mixer_volume = 0
        change_volume = False
        sleep_duration = 0.5
        start_volume_date = 0
        previous_time = 0
        player_pos = 0
        players_str="players"

        server_status = self.my_server.cls_server_status()

        while True:
            if self.local_IP == "0.0.0.0":
                self.local_IP = self.get_my_ip()
            
            for i in range (10):
                players = self.get_players_info()
                today = datetime.today()
                strToPrint = "host "
                if today.second % 2:
                    strToPrint = strToPrint + "* "
                else:
                    strToPrint = strToPrint + "- "
                
                if len(players[1]) < 10:
                    strToPrint = strToPrint + "players=" + str(len(players[1]))
                else:
                    strToPrint = strToPrint + "play.= " + str(len(players[1]))

                self.lcd.lcd_display_string(strToPrint, 1)    
                self.lcd.lcd_display_string(self.local_IP, 2)
                sleep(0.8)

            players = self.get_players_info()
            # self.lcd.lcd_display_string("player " + str(len(players[1]))  , 1)
            i = 1
            for player in players[1]:
                if player['isplaying'] == 1:
                    self.lcd.lcd_display_string(str(i) + "P/" + str(len(players[1])) + " " + player['name'], 1)
                else:
                    self.lcd.lcd_display_string(str(i) + "/" + str(len(players[1])) + " " + player['name'], 1)
                self.lcd.lcd_display_string(player['ip'].split(':')[0]  , 2)
                sleep(3)
                i = i + 1
            
            
if __name__ == "__main__":
    """
    This is the main:
    - grabbing params from CLI 
    - 
    """

    print("--- LMS API Requester ---")
    print("      For 16*2 LCD")
    print("please use -h for help")
    print("Enjoy using LMS!")

    description = "LMS API Requester"
    server_help = "ip and port for the server. something like 192.168.1.192:9000"
    lcd_help = "LCD address something like 0x3f"
    i2c_help = "i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2"
    display_mode_help = "set to volume or bitrate"
    player_name_help = "player name to lock the LCD on it"

    parser = argparse.ArgumentParser(description = description)
    parser.add_argument("-s","--server", type=str, default="192.168.1.193:9000", help = server_help)
    parser.add_argument("-l","--lcd", type=lambda x: int(x, 0), default=0x3f, help = lcd_help)
    parser.add_argument("-i","--i2c_port", type=int, default=1, help = i2c_help)
    parser.add_argument("-v","--virtual_lcd", type=str, default="no", help = lcd_help)
    parser.add_argument("-d","--display_mode", type=str, default="", help = display_mode_help)
    parser.add_argument("-p","--player_name",type=str, default="", help = player_name_help)

    args = parser.parse_args()

    # we are supposed to run this to the end of time
    while True:
        myLCD = LCD16(args.server, 
                      args.lcd, 
                      args.i2c_port,
                      args.virtual_lcd,
                      args.display_mode,
                      args.player_name)
        try:
            myLCD.main_loop()
        except Exception as err:
            print(str(err))
            myLCD = None        
