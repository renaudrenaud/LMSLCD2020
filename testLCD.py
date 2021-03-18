"""
Using I2C LCD 2*16 to show information from the LMS
RC 2020-01-15

To debug with codium we need root for LCD Access:
sudo codium --user-data-dir="~/.vscode-root"

2020-03-18 V1.2.0: add sleep in mm:ss
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
import platform

def get_players_info(playername:str="")->dict: 
    """
    Grab the information for the first player playing music

    Parameters:
        None

    Returns:
        dict: LMS Player
    """
    try:
        players = my_server.cls_players_list()
        for player in players:
            # print(player["name"])
            if playername == player['name']:
                return player, players
            elif player["isplaying"] == 1 and playername == "":
                return player, players
    except Exception  as err:
        print(err)
        return None, None 
    
    return None, players

def get_from_loop(source_list, key_to_find)->str:
    """
    iterate the list and return the value when the key_to_find is found

    Parameters:
        source_list (list of dict): each element conatins a key and a value
        key_to_find (str): the key to find in the list

    Returns:
        str: the value found or ""

    """
    ret = ""
    for elt in source_list:
        if key_to_find in elt.keys():
            ret = elt[key_to_find]
            break

    return ret

def screen_lms_info():
    """
    Print some info on the LCD when connection to the LMS

    """
    if type(server_status) is not dict:
        lcd.lcd_display_string("LMS not found", 1)
        lcd.lcd_display_string("no player.",2)
    else:
        server = server_status["result"]
        lcd.lcd_display_string("LMS :" + server["version"],1)
        lcd.lcd_display_string("Players ct:" + str(server["player count"]),2)

description = "LMS API Requester"
server_help = "ip and port for the server. something like 192.168.1.192:9000"
lcd_help = "LCD address something like 0x3f"
i2c_help = "i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2"
display_mode_help = "set to volume or clock to show volume or clock"
player_name_help = "player name to lock the LCD on it"

parser = argparse.ArgumentParser(description = description)
parser.add_argument("-s","--server", type=str, default="192.168.1.192:9000", help = server_help)
parser.add_argument("-l","--lcd", type=lambda x: int(x, 0), default=0x3f, help = lcd_help)
parser.add_argument("-i","--i2cport", type=int, default=1, help = i2c_help)
parser.add_argument("-v","--virtuallcd", type=str, default="no", help = lcd_help)
parser.add_argument("-d","--displaymode", type=str, default="", help = display_mode_help)
parser.add_argument("-p","--playername",type=str, default="", help = player_name_help)

args = parser.parse_args()

print (platform.platform())
if "Windows" in platform.platform() or args.virtuallcd == "yes":
    import no_lcddriver
    lcd = no_lcddriver.lcd(address = args.lcd) 
else:
    import lcddriver
    lcd = lcddriver.lcd(address = args.lcd, i2c_port = args.i2cport)
    lcd.lcd_display_string("     C&R ID     ", 1)
    lcd.lcd_display_string("   Audiofolies  " , 2)
    sleep(3)

my_server = LmsServer(args.server)
server_status = my_server.cls_server_status()

screen_lms_info()

sleep(3)

last_song = {}
album = ""
runner = "+"
decal = 0
song_info = None
mixer_volume = 0
change_volume = False
sleep_duration = 0.2
start_volume_date = 0

while True:
    today = datetime.today()

    if args.displaymode != "clock":
        if today.second == 0:
            server_status = my_server.cls_server_status()
        if change_volume is False:
            player_info, players = get_players_info(args.playername)

    if args.displaymode != "clock" and player_info is not None and player_info['isplaying'] ==1 and type(server_status) is dict:
        # sec = int(today.strftime("%S"))
        if runner == "+":
            runner = "*"
        else:
            runner = "+"
                        
        player = my_server.cls_player_current_title_status(player_info['playerid'])

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
     
        song_index = int(player["playlist_cur_index"]) 
        song = player["playlist_loop"][song_index]
    
        if int(song["id"]) != 0:
            # When id is positive, it comes from LMS database
            if (song_info is None or song["id"] != song_info["songinfo_loop"][0]["id"]) or int(song["id"]) < 0:
                song_info = my_server.cls_song_info(song["id"], player_info['playerid'])
                if song != last_song:
                    album = get_from_loop(song_info["songinfo_loop"], "album")
                    # if "artist" in song_info["songinfo_loop"][4].keys():
                    artist = get_from_loop(song_info["songinfo_loop"], "artist")
                    if len(artist) == 0:
                        artist = get_from_loop(song_info["songinfo_loop"], "albumartist")
                    song_title = get_from_loop(song_info["songinfo_loop"], "title")
                    if "current_title" in player.keys():
                        current_title = player['current_title']
                    else:
                        current_title = ""
                    
                    samplesize = get_from_loop(song_info["songinfo_loop"], "samplesize")
                    if samplesize == "":
                        samplesize = 'N/A'

                    samplerate = get_from_loop(song_info["songinfo_loop"], "samplerate")
                    if samplerate == "":
                        samplerate = "N/A"
                    else:
                        samplerate = str(int(int(samplerate) / 1000)) + "k"
                    
                    bitrate = get_from_loop(song_info["songinfo_loop"], "bitrate")
                    file_format = get_from_loop(song_info["songinfo_loop"], "type")

                    duration = get_from_loop(song_info["songinfo_loop"],"duration") 
                    dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))
                    track_pos = str(int(player['playlist_cur_index']) + 1) + "/" + str(player['playlist_tracks']) 
                    decal = 0
                    decal1 = 0
                    decal2 = 0

        if args.displaymode == "volume" or change_volume == True:
            lcd.lcd_display_string("Vol" + chr(255) * int(mixer_volume / 10) + chr(95) * (10 -(int(mixer_volume / 10))) + str(mixer_volume)  , 1)
            # lcd.lcd_display_string(("B:" + samplesize + " - F:" + samplerate + ' ' * 20)[:16], 2)
            lcd.lcd_display_string(("B:" + samplesize + "-F:" + samplerate + ' ' + file_format + ' ' * 16)[:16], 2)
            sleep(sleep_duration)
        elif player["time"] < 3:
            # When track time is less then 3 seconds it means a new song
            lcd.lcd_display_string(player['player_name'], 1)
            try:
                lcd.lcd_display_string(player['player_ip'].split(":")[0], 2)   
            except:
                pass
            
            sleep(2)     

        elif player["time"] < 10:    
            max_car1 = len(artist) -16
            max_car2 = len(album) -16
            if decal1 > max_car1:
                decal1 = 0
            if decal2 > max_car1:
                decal2 = 0
            lcd.lcd_display_string(artist[decal1:16 + decal], 1)
            lcd.lcd_display_string(album[decal2:16 + decal], 2)
    
        elif player["time"] < 15:
            lcd.lcd_display_string(("B:" + samplesize + "-F:" + samplerate + ' ' + file_format + ' ' * 16)[:16], 1)
            lcd.lcd_display_string((bitrate + ' ' * 16)[:16], 2)
            
        elif player["time"] < 20:

            lcd.lcd_display_string("durat-:" + dur_hh_mm_ss, 1)
            lcd.lcd_display_string("tracks: " + track_pos, 2)

        else:
            if 'will_sleep_in' in player.keys():
                lcd.lcd_display_string(strftime("sleep in %M:%S", gmtime(player['will_sleep_in'])), 1)
            else:
                lcd.lcd_display_string(today.strftime("%d/%m/%y  %H:%M") + runner, 1)
            
            title = album + " - " + song_title 
            
            title = "Alb: " + album + " - Tit: " + song_title + " (" + track_pos + ") - Art: " + artist
            max_car = len(title) - 16
            if decal > max_car:
                decal = 0  
            lcd.lcd_display_string(title[decal:16 + decal], 2)
            decal = decal + 1
        last_song = song
        sleep(sleep_duration)
    else:
        today = datetime.today()
        lcd.lcd_display_string(today.strftime("Clock %d/%m/%Y"), 1)
        lcd.lcd_display_string(today.strftime("Time  %H:%M:%S"), 2)
        sleep(.8)
