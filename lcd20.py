"""
Using I2C LCD 2*16 to show information from the LMS
RC 2020-01-15

To debug with codium we need root for LCD Access:
sudo codium --user-data-dir="~/.vscode-root"
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

description = "LMS API Requester"
server_help = "ip and port for the server. something like 192.168.1.192:9000"
lcd_help = "LCD address something like 0x3f"
parser = argparse.ArgumentParser(description = description)
parser.add_argument("-s","--server", type=str, default="192.168.1.192:9000", help = server_help)
parser.add_argument("-l","--lcd", type=lambda x: int(x, 0), default=0x3f, help = lcd_help)
parser.add_argument("-v","--virtuallcd", type=str, default="no", help = lcd_help)

args = parser.parse_args()

# if 
# windows, we cannot use the LCD
# instead we print on the same line
print (platform.platform())
if "Windows" in platform.platform() or args.virtuallcd == "yes":
    import no_lcddriver
    lcd = no_lcddriver.lcd(address = args.lcd, columns=20) 
else:
    import lcddriver
    lcd = lcddriver.lcd(address = args.lcd, columns=20)

lcd.lcd_clear()

myServer = LMS_SERVER(args.server)

def getPlayersInfo()->dict: 
    """
    Grab the information for the first player playing music

    Parameters:
        None

    Returns:
        dict: LMS Player
    """
    players = myServer.cls_players_list()
    for player in players:
        # print(player["name"])
        if player["isplaying"] == 1:
            return player, players
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


last_song = {}
album = ""
runner = "+"
decal = 0
song_info = None
mixer_volume = 0
change_volume = False
sleep_duration = 0.8

while True:
    seconds = time()
    today = datetime.today()
    player_info, players = getPlayersInfo()
    if player_info is not None:
        # sec = int(today.strftime("%S"))
        if runner == "+":
            runner = "*"
        else:
            runner = "+"
                        
        player = myServer.cls_player_current_title_status(player_info['playerid'])
        if player["mixer volume"] != mixer_volume:
            if mixer_volume == 0:
                mixer_volume = player["mixer volume"]
            else:
                mixer_volume = player["mixer volume"]
                lcd.lcd_display_string("Volume " + str(mixer_volume) + " /100" , 2)
                sleep(0.2)
                change_volume = True
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
                    samplesize = get_from_loop(song_info["songinfo_loop"], "samplesize")
                    samplerate = get_from_loop(song_info["songinfo_loop"], "samplerate")
                    bitrate = get_from_loop(song_info["songinfo_loop"], "bitrate")

                    duration = get_from_loop(song_info["songinfo_loop"],"duration") 
                    dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))

                    


                    track_pos = str(int(player['playlist_cur_index']) + 1) + "/" + str(player['playlist_tracks']) 
                    decal = 0
                    decal1 = 0
                    decal2 = 0

        if change_volume == True:
            pass
        elif player["time"] < 3:
            # When track time is less then 3 seconds it means a new song
            lcd.lcd_display_string(player['player_name'], 1)
            lcd.lcd_display_string(player['player_ip'].split(":")[0], 2)    
            sleep(2)     

        elif player["time"] < 10:    
            max_car1 = len(artist) -20
            max_car2 = len(album) -20
            if decal1 > max_car1:
                decal1 = 0
            if decal2 > max_car1:
                decal2 = 0
            lcd.lcd_display_string(artist[decal1:20 + decal], 1)
            lcd.lcd_display_string(album[decal2:20 + decal], 2)
      
        elif player["time"] < 15:
            lcd.lcd_display_string(("B:" + samplesize + " - F:" + samplerate + ' ' * 20)[:20], 1)
            lcd.lcd_display_string((bitrate + ' ' * 20)[:20], 2)
            
        elif player["time"] < 20:

            lcd.lcd_display_string("durat-:" + dur_hh_mm_ss, 1)
            lcd.lcd_display_string("tracks: " + track_pos, 2)

        else:
            lcd.lcd_display_string(today.strftime("%d/%m/%y  %H:%M:%S"), 1)
            lcd.lcd_display_string(artist, 2)
            title = album + " - " + song_title 
            elapsed = strftime("%M:%S", gmtime(player["time"]))
            if len(artist) > 20: 
                title = "Alb: " + album + " - Tit: " + song_title + " - Art: " + artist + "     "
            else:
                title = "Alb: " + album + " - Tit: " + song_title + "     "
            max_car = len(title) - 20
            if decal > max_car:
                decal = 0  
            lcd.lcd_display_string(title[decal:20 + decal], 3)
            
            lcd.lcd_display_string("T " + track_pos + " " + elapsed + " " + str(round(100 / int(duration) * player["time"])) + "%", 4)
            
            decal = decal + 1
        last_song = song
        sleep(sleep_duration)
    else:
        # Just a clock !
        today = datetime.today()
        lcd.lcd_display_string(today.strftime("%d/%m/%Y  %H:%M:%S"), 1)
        lcd.lcd_display_string(" ", 2)
        lcd.lcd_display_string("s=" + args.server, 3)
        if len(players) > 0:
            lcd.lcd_display_string("Players count: " + str(len(players)), 4)
        else:
            lcd.lcd_display_string("Player not found!", 4)
        sleep(.1)
