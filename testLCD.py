"""
Using I2C LCD 2*16 to show information from the LMS
RC 2020-01-15

To debug with codium we need root for LCD Access:
sudo codium --user-data-dir="~/.vscode-root"

2021-11-19 v2.3.2: take in account player with no mixer volume! 
2021-05-16 v2.3.1: search IP and print at launch
2021-04-15 v2.3.0: print the number of players on 1 car enf of line 1
2021-04-11 v2.2.0: replace accented characters, LCD cannot print them
2021-04-03 v2.1.0: TSJ Jazz has a fixed duration for their track with value = 0.875
                    so the LCD was stucked on the first screen < 3 seconds!
2021-03-21 v2.0.0: using a class now and supposely bullet proof
2021-03-18 V1.2.0: add 
                    - sleep in mm:ss
                    - rescan status
2021-03-15 v1.1.0: add the "type" format ie: aac or flc or dsf...
2021-03-21 v1.0.1: - better volume management
                   - remove spaces for track on track, not required and we have only 16 char!
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
    
        self.__version__ = "v2.3.1"
        
        self.player_name = player_name
        self.display_mode = display_mode

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
            self.lcd.lcd_display_string("Local IP:", 1)
            self.lcd.lcd_display_string(self.get_my_ip(), 2)
            sleep(5)

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
            for player in players:
                if playername == player['name']:
                    return player, players
                elif player["isplaying"] == 1 and playername == "":
                    return player, players
        except Exception  as err:
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
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    
    
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
            today = datetime.today()
            if self.display_mode != "clock":
                if today.second == 0:
                    server_status = self.my_server.cls_server_status()
                if change_volume is False:
                    player_info, players = self.get_players_info(self.player_name)

            if self.display_mode != "clock" and player_info is not None and player_info['isplaying'] ==1 and type(server_status) is dict:
                if self.my_server.cls_server_is_scanning():
                    if runner != "S":
                        runner = "S"
                    else:
                        runner = "s"
                else:
                    if runner != "*":
                        runner = "*"
                    else:
                        runner = "+"
                                
                player = self.my_server.cls_player_current_title_status(player_info['playerid'])

                if "mixer_volume" in player:
                    if player["mixer volume"] != mixer_volume or change_volume is True:
                        if mixer_volume == 0:
                            mixer_volume = player["mixer volume"]
                        else:
                            if player["mixer volume"] != mixer_volume:
                                start_volume_date = datetime.now()
                            
                            mixer_volume = player["mixer volume"]
                            
                            if change_volume is False:
                                start_volume_date = datetime.now()  
                                change_volume = True
                                old_sleep_duration = sleep_duration
                                sleep_duration = 0
                            
                            else:
                                if (datetime.now() - start_volume_date).seconds > 3:
                                    change_volume = False
                                    start_volume_date = 0
                                    sleep_duration = old_sleep_duration

                    else:
                        change_volume = False
                else:
                    change_volume = False
                song_index = int(player["playlist_cur_index"]) 
                song = player["playlist_loop"][song_index]
            
                if int(song["id"]) != 0:
                    # When id is positive, it comes from LMS database
                    if (song_info is None or song["id"] != song_info["songinfo_loop"][0]["id"]) or int(song["id"]) < 0:
                        song_info = self.my_server.cls_song_info(song["id"], player_info['playerid'])
                        if song != last_song:
                            album = self.get_from_loop(song_info["songinfo_loop"], "album")
                            # if "artist" in song_info["songinfo_loop"][4].keys():
                            artist = self.get_from_loop(song_info["songinfo_loop"], "artist")

                            if len(artist) == 0:
                                artist = self.get_from_loop(song_info["songinfo_loop"], "albumartist")
                            if len(artist) == 0:
                                artist = song["title"]

                            song_title = self.get_from_loop(song_info["songinfo_loop"], "title")
                            # current_title = ""
                            # if "current_title" in player.keys():
                                # current_title = player['current_title']
                            
                            samplesize = self.get_from_loop(song_info["songinfo_loop"], "samplesize")
                            if samplesize == "":
                                samplesize = "N/A"
                            
                            samplerate = self.get_from_loop(song_info["songinfo_loop"], "samplerate")
                            if samplerate == "":
                                samplerate = "N/A"
                            else:
                                samplerate = str(int(int(samplerate) / 1000)) + "k"
                            
                            bitrate = self.get_from_loop(song_info["songinfo_loop"], "bitrate")
                            file_format = self.get_from_loop(song_info["songinfo_loop"], "type")

                            duration = self.get_from_loop(song_info["songinfo_loop"],"duration") 
                            dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))
                            track_pos = str(int(player['playlist_cur_index']) + 1) + "/" + str(player['playlist_tracks']) 
                            decal = 0
                            decal1 = 0
                            decal2 = 0

                # remove accented chars, LCD cannot write them
                artist = unicodedata.normalize('NFD', artist).encode('ascii', 'ignore').decode("utf-8")
                album = unicodedata.normalize('NFD', album).encode('ascii', 'ignore').decode("utf-8")
                song_title = unicodedata.normalize('NFD', song_title).encode('ascii', 'ignore').decode("utf-8")

                if self.display_mode == "volume" or change_volume == True:
                    self.lcd.lcd_display_string("Vol" + chr(255) * int(mixer_volume / 10) + chr(95) * (10 -(int(mixer_volume / 10))) + str(mixer_volume)  , 1)
                    # lcd.lcd_display_string(("B:" + samplesize + " - F:" + samplerate + ' ' * 20)[:16], 2)
                    self.lcd.lcd_display_string(("B:" + samplesize + "-F:" + samplerate + ' ' + file_format + ' ' * 16)[:16], 2)
                    
                    
                elif player["time"] < 3 and player["time"] != previous_time:
                    # When track time is less then 3 seconds it means a new song
                    previous_time = player["time"]
                    self.lcd.lcd_display_string(player['player_name'], 1)
                    try:
                        self.lcd.lcd_display_string(player['player_ip'].split(":")[0], 2)   
                    except:
                        pass
                    
                    sleep(2)     

                elif player["time"] < 10 and player["time"] != previous_time:    
                    max_car1 = len(artist) -16
                    # max_car2 = len(album) -16
                    if decal1 > max_car1:
                        decal1 = 0
                    if decal2 > max_car1:
                        decal2 = 0
                    self.lcd.lcd_display_string(artist[decal1:16 + decal], 1)
                    self.lcd.lcd_display_string(album[decal2:16 + decal], 2)
            
                elif player["time"] < 15 and player["time"] != previous_time:
                    self.lcd.lcd_display_string(("B:" + samplesize + "-F:" + samplerate + ' ' + file_format + ' ' * 16)[:16], 1)
                    self.lcd.lcd_display_string((bitrate + ' ' * 16)[:16], 2)
                    
                elif player["time"] < 20 and player["time"] != previous_time:

                    self.lcd.lcd_display_string("durat-:" + dur_hh_mm_ss, 1)
                    self.lcd.lcd_display_string("tracks: " + track_pos, 2)

                else:
                    if 'will_sleep_in' in player.keys():
                        # sleep function is activated!
                        self.lcd.lcd_display_string(strftime("sleep in %M:%S", gmtime(player['will_sleep_in'])), 1)
                    else:
                        # some code to print number of players on 1 char!
                        if player_pos < len(players_str) and player_pos >= 0:
                            player_count = players_str[player_pos]
                            player_pos = player_pos + 1
                        elif player_pos >= -5 and player_pos < len(players_str):
                            player_count = str(len(players))
                            player_pos = player_pos + 1
                        else:
                            player_count = str(len(players))
                            player_pos = - 5 

                        self.lcd.lcd_display_string(today.strftime("%d/%m/%y %H:%M") + runner + player_count, 1)
                        
                    if self.my_server.cls_server_is_scanning():
                        scan = self.my_server.cls_server_scanning_status()
                        title = "scaning " + scan['steps'] + " " + scan['totaltime'] + "...  "
                    else:
                        title = track_pos + " Tit: " + song_title  
                        if len(album) > 0:
                            title = title + " - Alb: " + album  
                        if len(artist) > 0:
                            title = title + " - Art: " + artist  
                        title = title + "  "
                    
                    max_car = len(title) - 16
                    if decal > max_car:
                        decal = 0  
                    self.lcd.lcd_display_string(title[decal:16 + decal], 2)
                    decal = decal + 1
                last_song = song
                sleep(sleep_duration)
            else:
                today = datetime.today()
                self.lcd.lcd_display_string(today.strftime("Clock %d/%m/%Y"), 1)
                self.lcd.lcd_display_string(today.strftime("Time  %H:%M:%S"), 2)
                sleep(.8)

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
    parser.add_argument("-v","--virtual_lcd", type=str, default="yes", help = lcd_help)
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
