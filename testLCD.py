"""
A test for the I2C LCD
RC 2020-01-15

Because we want to debug with codium and need root for LCD Access:
sudo codium --user-data-dir="~/.vscode-root"
"""

import lcddriver
import argparse
from datetime import datetime
from datetime import timedelta
from time import sleep
from time import time
from time import strftime
from time import gmtime
from lmsmanager import LMS_SERVER

description = "LMS API Requester"
server_help = "ip and port for the server. something like 192.168.1.192:9000"
lcd_help = "LCD address something like 0x3f"
parser = argparse.ArgumentParser(description = description)
parser.add_argument("-s","--server", type=str, default="192.168.1.192:9000", help = server_help)
parser.add_argument("-l","--lcd", type=str, default=0x3f, help = lcd_help)



args = parser.parse_args()

lcd = lcddriver.lcd(address = args.lcd)
lcd.lcd_clear()

myServer = LMS_SERVER(args.server)

def getPlayerInfo()->dict: 
    """
    Grab the information for the first player playing music

    - Input
    : None

    - Output
    : LMS Player
    """
    players = myServer.cls_players_list()
    for player in players:
        if player["isplaying"] == 1:
            return player

    # print("Waoo ->" + player['name'])
    # myServer.cls_player_status(player['playerid'])

print("hello")

song_info = None
runner = "+P"

while True:
    seconds = time()
    today = datetime.today()
    player = getPlayerInfo()
    if player is not None:
        sec = int(today.strftime("%S"))
        if runner == "+P":
            runner = "-p"
        else:
            runner = "+P"
                        
        player = myServer.cls_player_current_title_status(player['playerid'])
        song_index = int(player["playlist_cur_index"]) 
        song = player["playlist_loop"][song_index]
        if song_info is None or song["id"] != song_info["songinfo_loop"][0]["id"]:
            song_info = myServer.cls_song_info(song["id"])
                
        if player["time"] < 3:
            lcd.lcd_display_string("LMS sends music>", 1)    
            lcd.lcd_display_string(player['player_name'], 2)
        
        elif player["time"] < 10:
            song_info = myServer.cls_song_info(song["id"])
            lcd.lcd_display_string((song_info["songinfo_loop"][4]["artist"]+ ' ' * 20)[:16], 1)
            lcd.lcd_display_string((song_info["songinfo_loop"][1]["title"]+ ' ' * 20)[:16], 2)
        elif player["time"] < 20:
            
            lcd.lcd_display_string("bt " + (song_info["songinfo_loop"][12]["bitrate"]+ ' ' * 20)[:16], 1)
            lcd.lcd_display_string("sl rate:" + (song_info["songinfo_loop"][17]["samplerate"]+ ' ' * 20)[:16], 2)
            
        elif player["time"] < 25:
            duration = song_info["songinfo_loop"][8]["duration"] 
            # dur_hh_mm_ss = str(timedelta(seconds=duration))
            dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(duration))
            lcd.lcd_display_string("durat:" + (dur_hh_mm_ss +  ' ' * 20)[:16], 1)
            track_pos = str(int(player['playlist_cur_index']) + 1) + " / " 
            lcd.lcd_display_string("tracks: " + track_pos + (str(player['playlist_tracks']) + ' ' * 20)[:16], 2)
        else:
            lcd.lcd_display_string(today.strftime("%d/%m/%y %H:%M") + runner, 1)
            lcd.lcd_display_string((song['title'] + ' ' * 20)[:16], 2)
    else:
        today = datetime.today()
        lcd.lcd_display_string(today.strftime("Clock %d/%m/%Y"), 1)
        lcd.lcd_display_string(today.strftime("No play %H:%M:%S"), 2)
    sleep(.8)
