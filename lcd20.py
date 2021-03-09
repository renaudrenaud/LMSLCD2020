"""
Using I2C LCD 2*16 to show information from the LMS
RC 2020-01-15

To debug with codium we need root for LCD Access:
sudo codium --user-data-dir="~/.vscode-root"

2021-03-21 V 1.0.1: - better volume management
                    - added params playername and displaymode
"""

import argparse
from datetime import datetime
from datetime import timedelta
from time import sleep
from time import time
from time import strftime
from time import gmtime
from typing import ChainMap
from lmsmanager import LMS_SERVER
import platform

def getPlayersInfo(playername:str="")->dict: 
    """
    Grab the information for the first player playing music

    Parameters:
        None

    Returns:
        dict: LMS Player
    """
    try:
        players = myServer.cls_players_list()
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
        lcd.lcd_display_string("LMS not found", 3)
        lcd.lcd_display_string("no player.",4)
    else:
        server = server_status["result"]
        lcd.lcd_display_string("LMS version:" + server["version"],3)
        lcd.lcd_display_string("Players:" + str(server["player count"]),4)

description = "LMS API Requester"
server_help = "ip and port for the server. something like 192.168.1.192:9000"
lcd_help = "LCD address something like 0x3f"
i2c_help = "i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2"
display_mode_help = "set to volume to show volume"
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
    lcd = no_lcddriver.lcd(address = args.lcd, columns=20) 
else:
    import lcddriver
    lcd = lcddriver.lcd(address = args.lcd, columns=20)
    lcd.lcd_clear()
    lcd.lcd_display_string("      C&R ID ", 1)
    lcd.lcd_display_string("    Audiofolies" , 2)
    lcd.lcd_display_string("sites.google.com/",3)
    lcd.lcd_display_string("view/audiofolies",4)
    sleep(4)

myServer = LMS_SERVER(args.server)
server_status = myServer.cls_server_status()

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
    if today.second == 0:
        server_status = myServer.cls_server_status()
    if change_volume is False:
        player_info, players = getPlayersInfo(args.playername)

    player_info, players = getPlayersInfo()
    if player_info is not None and player_info['isplaying'] ==1 and type(server_status) is dict:

        player = myServer.cls_player_current_title_status(player_info['playerid'])
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
                song_info = myServer.cls_song_info(song["id"], player_info['playerid'])
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
                    
                    if len(get_from_loop(song_info["songinfo_loop"], "remote_title")) > 0:
                        current_title = get_from_loop(song_info["songinfo_loop"], "remote_title") + "-" + current_title

                    if len(current_title) == 0:
                        current_title = song_title

                    samplesize = get_from_loop(song_info["songinfo_loop"], "samplesize")
                    samplerate = get_from_loop(song_info["songinfo_loop"], "samplerate")
                    bitrate = get_from_loop(song_info["songinfo_loop"], "bitrate")

                    duration = get_from_loop(song_info["songinfo_loop"],"duration") 
                    dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))

                    track_pos = str(int(player['playlist_cur_index']) + 1) + "/" + str(player['playlist_tracks']) 
                    decal = 0
                    decal1 = 0
                    decal2 = 0

        if args.displaymode == "volume" and player["time"] > 15 or change_volume == True:
            lcd.lcd_display_string("Vol" + chr(255) * int(mixer_volume / 10) + chr(95) * (10 -(int(mixer_volume / 10))) + str(mixer_volume)  , 1)
            lcd.lcd_display_string(("B:" + samplesize + " - F:" + samplerate + ' ' * 20)[:16], 2)
            sleep(sleep_duration)
        elif player["time"] < 3:
            # When track time is less then 3 seconds it means a new song
            lcd.lcd_display_string(player['player_name'], 1)
            try:
                lcd.lcd_display_string(player['player_ip'].split(":")[0], 2)  
            except:
                pass
            
            lcd.lcd_display_string(artist, 3)
            lcd.lcd_display_string(album, 4)  
            sleep(2)     

        elif player["time"] < 10:    
            max_car1 = len(artist) -20
            max_car2 = len(album) -20
            if decal1 > max_car1:
                decal1 = 0
            if decal2 > max_car1:
                decal2 = 0
            lcd.lcd_display_string(artist[decal1:20 + decal], 3)
            lcd.lcd_display_string(album[decal2:20 + decal], 4)
      
        elif player["time"] < 15:
            lcd.lcd_display_string(("B:" + samplesize + " - F:" + samplerate + ' ' * 20)[:20], 1)
            lcd.lcd_display_string((bitrate + ' ' * 20)[:20], 2)
            
        elif player["time"] < 20:

            lcd.lcd_display_string("durat-:" + dur_hh_mm_ss, 1)
            lcd.lcd_display_string("tracks: " + track_pos, 2)

        else:
            lcd.lcd_display_string(today.strftime("%d/%m/%y  %H:%M:%S"), 1)
            if len(artist) > 0: 
                lcd.lcd_display_string(artist, 2)
            else:
                lcd.lcd_display_string((bitrate + ' ' * 20)[:20], 2)
            title = album + " - " + current_title 
            if int(duration) > 0:
                elapsed = strftime("%M:%S", gmtime(player["time"])) + "-" + strftime("%M:%S", gmtime(int(duration)))
            else:
                elapsed = strftime("%M:%S", gmtime(player["time"]))

            if len(artist) > 20: 
                title = "Alb: " + album + " - Tit: " + current_title + " - Art: " + artist + "     "
            else:
                title = "Alb: " + album + " - Tit: " + current_title + "     "
            max_car = len(title) - 20
            if decal > max_car:
                decal = 0  
            lcd.lcd_display_string(title[decal:20 + decal], 3)
            
            lcd.lcd_display_string("" + track_pos + " " + elapsed, 4)
            
            decal = decal + 1
        last_song = song
        sleep(sleep_duration)
    else:
        # Just a clock !
        today = datetime.today()
        if type(server_status) is dict:
            lcd.lcd_display_string(today.strftime("%d/%m/%Y  %H:%M:%S"), 1)
            lcd.lcd_display_string("LMS v" + server_status["result"]["version"],2)
            lcd.lcd_display_string("" + args.server, 3)
            if players is not None:
                if len(players) > 0:
                    lcd.lcd_display_string("Players count: " + str(len(players)), 4)
                else:
                    lcd.lcd_display_string("Player not found!", 4)
                sleep(.1)
            else:
                lcd.lcd_display_string("No player",4)
        else:
            lcd.lcd_display_string(today.strftime("%d/%m/%Y  %H:%M"), 1)
            lcd.lcd_display_string("LMS not connected on",2)
            lcd.lcd_display_string(args.server, 3)
            lcd.lcd_display_string("no player", 4)
