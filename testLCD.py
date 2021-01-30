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
from lmsmanager import LMS_SERVER
import platform

description = "LMS API Requester"
server_help = "ip and port for the server. something like 192.168.1.192:9000"
lcd_help = "LCD address something like 0x3f"
parser = argparse.ArgumentParser(description = description)
parser.add_argument("-s","--server", type=str, default="192.168.1.192:9000", help = server_help)
parser.add_argument("-l","--lcd", type=str, default=0x3f, help = lcd_help)

args = parser.parse_args()

# if windows, we cannot use the LCD
# instead we print on the same line
print (platform.platform())
if "Windows" in platform.platform():
    import no_lcddriver
    lcd = no_lcddriver.lcd(address = args.lcd) 
else:
    import lcddriver
    lcd = lcddriver.lcd(address = args.lcd)

lcd.lcd_clear()

myServer = LMS_SERVER(args.server)

def getPlayerInfo()->dict: 
    """
    Grab the information for the first player playing music

    Parameters:
        None

    Returns:
        dict: LMS Player
    """
    players = myServer.cls_players_list()
    for player in players:
        if player["isplaying"] == 1:
            return player


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
runner = "+"
decal = 0
song_info = None

while True:
    seconds = time()
    today = datetime.today()
    player = getPlayerInfo()
    if player is not None:
        # sec = int(today.strftime("%S"))
        if runner == "+":
            runner = "*"
        else:
            runner = "+"
                        
        player = myServer.cls_player_current_title_status(player['playerid'])
        song_index = int(player["playlist_cur_index"]) 
        song = player["playlist_loop"][song_index]

        if int(song["id"]) > 0:
            # When id is positive, it comes from LMS database
            if song_info is None or song["id"] != song_info["songinfo_loop"][0]["id"]:
                song_info = myServer.cls_song_info(song["id"])
                if "artist" in song_info["songinfo_loop"][4].keys():
                    artist = get_from_loop(song_info["songinfo_loop"], "artist")
                elif "albumartist" in song_info["songinfo_loop"][4].keys():
                    artist = get_from_loop(song_info["songinfo_loop"], "albumartist")
                song_title = get_from_loop(song_info["songinfo_loop"], "title")
                samplesize = get_from_loop(song_info["songinfo_loop"], "samplesize")
                samplerate = get_from_loop(song_info["songinfo_loop"], "samplerate")
                bitrate = get_from_loop(song_info["songinfo_loop"], "bitrate")

                duration = get_from_loop(song_info["songinfo_loop"],"duration") 
                dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(duration))
                track_pos = str(int(player['playlist_cur_index']) + 1) + " / " + str(player['playlist_tracks']) 

        else:
            # id is a negative value: prbably from radio?
            pass

        if player["time"] < 3:
            # When track time is less then 3 seconds it means a new song
            lcd.lcd_display_string(player['player_ip'].split(":")[0], 1)    
            lcd.lcd_display_string(player['player_name'], 2)
            decal = 0
            sleep(2)    
            
        elif player["time"] < 10:
            if int(song["id"]) > 0:
                lcd.lcd_display_string((artist + ' ' * 20)[:16], 1)
                lcd.lcd_display_string(( song_title + ' ' * 20)[:16], 2)
            else:
                lcd.lcd_display_string((player["current_title"]+ ' ' * 20)[:16], 1)
                lcd.lcd_display_string((song['title'] + ' ' * 20)[:16], 2)

        elif player["time"] < 20:
            if song_info is not None:
                # print some info on bits, frq and bitrate
                lcd.lcd_display_string(("B/F: " + samplesize + " / " + samplerate + ' ' * 20)[:16], 1)
                lcd.lcd_display_string((bitrate + ' ' * 20)[:16], 2)
            
        elif player["time"] < 25:
            if song_info is not None:
                lcd.lcd_display_string(("durat:" + dur_hh_mm_ss +  ' ' * 20)[:16], 1)
                lcd.lcd_display_string(("tracks: " + track_pos +  ' ' * 20)[:16], 2)
            else:
                lcd.lcd_display_string((player["current_title"]+ ' ' * 20)[:16], 1)
                lcd.lcd_display_string((song['title'] + ' ' * 20)[:16], 2)

        else:
            lcd.lcd_display_string(today.strftime("%d/%m/%y  %H:%M") + runner, 1)
            if len(song['title']) < 16:
                lcd.lcd_display_string((song['title'] + ' ' * 20)[:16], 2)
            else:
                max_car = len(song['title']) - 16
                if decal == max_car:
                    decal = 0  
                lcd.lcd_display_string(song['title'][decal:16 + decal], 2)
                decal = decal + 1
        last_song_id = song
    else:
        # Just a clock !
        today = datetime.today()
        lcd.lcd_display_string(today.strftime("Clock %d/%m/%Y"), 1)
        lcd.lcd_display_string(today.strftime("No play %H:%M:%S"), 2)
    sleep(.8)
