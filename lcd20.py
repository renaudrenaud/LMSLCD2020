"""
Using I2C LCD 2*16 to show information from the LMS
RC 2020-01-15


Depending on the OS we need root rights on i2c bus
And to debug with codium we need root for LCD Access:
sudo codium --user-data-dir="~/.vscode-root"

2021-04-11 v2.2.0: replace accented characters, LCD cannot print them
2021-04-03 v2.1.0: TSJ Jazz has a fixed duration for their track with value = 0.875
                    so the LCD was stucked on the first screen < 3 seconds!
2021-03-21 v2.0.0: using a class now and supposely bullet proof
2021-03-18 v1.3.0: add sleep in mm:ss when required for the player
2021-03-15 v1.2.0: add the "type" format ie: aac or flc or dsf...
2021-03-10 v1.1.1: code cleaning
2021-03-09 v1.1.0: - better volume management
                   - added params playername and displaymode
"""

import argparse
import platform
from datetime import datetime, timedelta
from time import gmtime, sleep, strftime, time
from typing import ChainMap

import unicodedata

from lmsmanager import LmsServer


class LCD20:
    """
    This is the class to manage the LCD 20x4
    """

    def __init__(
        self,
        server: str,
        lcd: int,
        i2c_port: int,
        virtual_lcd: str,
        display_mode: str,
        player_name: str,
    ):

        self.__version__ = "v2.0.0"

        self.player_name = player_name
        self.display_mode = display_mode

        self.my_server = LmsServer(server)
        # self.server_status = self.my_server.server_status()

        if "Windows" in platform.platform() or virtual_lcd == "yes":
            import no_lcddriver

            self.lcd = no_lcddriver.lcd(address=lcd, columns=20)
        else:
            import lcddriver

            self.lcd = lcddriver.lcd(address=lcd, columns=20, i2c_port=i2c_port)
            self.lcd.lcd_clear()
            self.lcd.lcd_display_string("      C&R ID ", 1)
            self.lcd.lcd_display_string("    Audiofolies", 2)
            self.lcd.lcd_display_string("sites.google.com/", 3)
            self.lcd.lcd_display_string("view/audiofolies", 4)
            sleep(2)

        self.screen_lms_info()
        sleep(3)

    def get_players_info(self, playername: str = "") -> dict:
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
                if playername == player["name"]:
                    return player, players
                elif player["isplaying"] == 1 and playername == "":
                    return player, players
        except Exception as err:
            print(err)
            return None, None

        return None, players

    def get_from_loop(self, source_list, key_to_find) -> str:
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
            self.lcd.lcd_display_string("no player.", 4)
        else:
            res = server["result"]
            self.lcd.lcd_display_string("LMS    : v" + res["version"], 1)
            self.lcd.lcd_display_string("Players: " + str(res["player count"]), 2)
            self.lcd.lcd_display_string("Albums : " + str(res["info total albums"]), 3)
            self.lcd.lcd_display_string("Songs  : " + str(res["info total songs"]), 4)

    def main_loop(self):
        last_song = {}
        album = ""

        decal = 0
        song_info = None
        mixer_volume = 0
        change_volume = False
        sleep_duration = 0.2
        start_volume_date = 0
        previous_time = 0

        server_status = self.my_server.cls_server_status()

        while True:
            today = datetime.today()
            if today.second == 0:
                server_status = self.my_server.cls_server_status()
            if change_volume is False:
                player_info, players = self.get_players_info(self.player_name)

            # player_info, players = get_players_info()
            if (
                player_info is not None
                and player_info["isplaying"] == 1
                and type(server_status) is dict
            ):

                player = self.my_server.cls_player_current_title_status(
                    player_info["playerid"]
                )
                if (
                    player is not None
                    and player["mixer volume"] != mixer_volume
                    or change_volume is True
                ):
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
                    if (
                        song_info is None
                        or song["id"] != song_info["songinfo_loop"][0]["id"]
                    ) or int(song["id"]) < 0:
                        song_info = self.my_server.cls_song_info(
                            song["id"], player_info["playerid"]
                        )
                        if song != last_song:
                            album = self.get_from_loop(
                                song_info["songinfo_loop"], "album"
                            )
                            # if "artist" in song_info["songinfo_loop"][4].keys():
                            artist = self.get_from_loop(
                                song_info["songinfo_loop"], "artist"
                            )
                            if len(artist) == 0:
                                artist = self.get_from_loop(
                                    song_info["songinfo_loop"], "albumartist"
                                )
                            if len(artist) == 0:
                                artist = song["title"]

                            song_title = self.get_from_loop(
                                song_info["songinfo_loop"], "title"
                            )
                            if "current_title" in player.keys():
                                current_title = player["current_title"]
                            else:
                                current_title = ""

                            if (
                                len(
                                    self.get_from_loop(
                                        song_info["songinfo_loop"], "remote_title"
                                    )
                                )
                                > 0
                            ):
                                current_title = (
                                    self.get_from_loop(
                                        song_info["songinfo_loop"], "remote_title"
                                    )
                                    + "-"
                                    + current_title
                                )

                            if len(current_title) == 0:
                                current_title = song_title

                            samplesize = self.get_from_loop(
                                song_info["songinfo_loop"], "samplesize"
                            )
                            if samplesize == "":
                                samplesize = "N/A"
                            samplerate = self.get_from_loop(
                                song_info["songinfo_loop"], "samplerate"
                            )
                            if samplerate == "":
                                samplerate = "N/A"
                            else:
                                samplerate = str(int(int(samplerate) / 1000)) + "k"

                            bitrate = self.get_from_loop(
                                song_info["songinfo_loop"], "bitrate"
                            )
                            file_format = self.get_from_loop(
                                song_info["songinfo_loop"], "type"
                            )

                            duration = self.get_from_loop(
                                song_info["songinfo_loop"], "duration"
                            )
                            dur_hh_mm_ss = strftime("%H:%M:%S", gmtime(int(duration)))

                            track_pos = (
                                str(int(player["playlist_cur_index"]) + 1)
                                + "/"
                                + str(player["playlist_tracks"])
                            )
                            decal = 0
                            decal1 = 0
                            decal2 = 0

                if (
                    self.display_mode == "volume"
                    and player["time"] > 15
                    or change_volume == True
                ):
                    self.lcd.lcd_display_string(
                        "Vol"
                        + chr(255) * int(mixer_volume / 10)
                        + chr(95) * (10 - (int(mixer_volume / 10)))
                        + str(mixer_volume)
                        + "%",
                        1,
                    )
                    self.lcd.lcd_display_string(
                        ("B:" + samplesize + " - F:" + samplerate + " " * 20)[:16], 2
                    )
                    sleep(sleep_duration)
                elif player["time"] < 3 and player["time"] != previous_time:
                    # When track time is less then 3 seconds it means a new song
                    previous_time = player["time"]
                    self.lcd.lcd_display_string(player["player_name"], 1)
                    self.lcd.lcd_display_string(player["player_ip"].split(":")[0], 2)
                    if len(artist) > 0:
                        self.lcd.lcd_display_string(artist, 3)
                        self.lcd.lcd_display_string(album, 4)
                    else:
                        self.lcd.lcd_display_string(
                            "LMS    : v" + server_status["result"]["version"], 3
                        )
                        self.lcd.lcd_display_string(
                            "Players: " + str(server_status["result"]["player count"]),
                            4,
                        )

                    sleep(2)

                    # remove accented chars, LCD cannot write them
                    artist = (
                        unicodedata.normalize("NFD", artist)
                        .encode("ascii", "ignore")
                        .decode("utf-8")
                    )
                    album = (
                        unicodedata.normalize("NFD", album)
                        .encode("ascii", "ignore")
                        .decode("utf-8")
                    )
                    song_title = (
                        unicodedata.normalize("NFD", song_title)
                        .encode("ascii", "ignore")
                        .decode("utf-8")
                    )

                elif player["time"] < 10 and player["time"] != previous_time:
                    max_car1 = len(artist) - 20
                    # max_car2 = len(album) -20
                    if decal1 > max_car1:
                        decal1 = 0
                    if decal2 > max_car1:
                        decal2 = 0

                    self.lcd.lcd_display_string(artist[decal1 : 20 + decal], 3)
                    self.lcd.lcd_display_string(album[decal2 : 20 + decal], 4)

                elif player["time"] < 15 and player["time"] != previous_time:
                    self.lcd.lcd_display_string(
                        (
                            "B:"
                            + samplesize
                            + " - F:"
                            + samplerate
                            + " "
                            + file_format
                            + " " * 20
                        )[:20],
                        1,
                    )
                    self.lcd.lcd_display_string((bitrate + " " * 20)[:20], 2)

                elif player["time"] < 20 and player["time"] != previous_time:

                    self.lcd.lcd_display_string("durat-:" + dur_hh_mm_ss, 1)
                    self.lcd.lcd_display_string("tracks: " + track_pos, 2)

                else:
                    if "will_sleep_in" in player.keys():
                        self.lcd.lcd_display_string(
                            strftime("sleep in %M:%S", gmtime(player["will_sleep_in"])),
                            1,
                        )
                    else:
                        self.lcd.lcd_display_string(
                            today.strftime("%d/%m/%y  %H:%M:%S"), 1
                        )

                    if self.my_server.cls_server_is_scanning():
                        scan = self.my_server.cls_server_scanning_status()
                        title = (
                            "scaning "
                            + scan["steps"]
                            + " "
                            + scan["totaltime"]
                            + "...  "
                        )
                    else:
                        title = album + " - " + song_title
                        title = (
                            "Alb: "
                            + album
                            + " - Tit: "
                            + song_title
                            + " ("
                            + track_pos
                            + ") - Art: "
                            + artist
                        )

                    if len(artist) > 0:
                        self.lcd.lcd_display_string(artist, 2)
                    else:
                        self.lcd.lcd_display_string(
                            ("bitrate: " + bitrate + " " * 20)[:20], 2
                        )
                    title = album + " - " + current_title
                    if int(duration) > 0:
                        elapsed = (
                            strftime("%M:%S", gmtime(player["time"]))
                            + "-"
                            + strftime("%M:%S", gmtime(int(duration)))
                        )
                    else:
                        elapsed = strftime("%M:%S", gmtime(player["time"]))

                    if len(artist) > 20:
                        title = (
                            "Alb: "
                            + album
                            + " - Tit: "
                            + current_title
                            + " - Art: "
                            + artist
                            + "     "
                        )
                    else:
                        title = "Alb: " + album + " - Tit: " + current_title + "     "
                    max_car = len(title) - 20
                    if decal > max_car:
                        decal = 0
                    self.lcd.lcd_display_string(title[decal : 20 + decal], 3)

                    if self.my_server.cls_server_is_scanning():
                        scan = self.my_server.cls_server_scanning_status()
                        scan_str = "scanning:" + scan["totaltime"] + "...  "
                        self.lcd.lcd_display_string(scan_str, 4)
                    else:
                        self.lcd.lcd_display_string("" + track_pos + " " + elapsed, 4)

                    decal = decal + 1
                last_song = song
                sleep(sleep_duration)
            else:
                # Just a clock !
                today = datetime.today()
                if type(server_status) is dict:
                    self.lcd.lcd_display_string(today.strftime("%d/%m/%Y %H:%M:%S"), 1)
                    self.lcd.lcd_display_string(
                        "LMS v" + server_status["result"]["version"], 2
                    )
                    if self.my_server.cls_server_is_scanning():
                        scan = self.my_server.cls_server_scanning_status()
                        scan_str = "scanning:" + scan["totaltime"] + "...  "
                        self.lcd.lcd_display_string(scan_str, 3)
                    else:
                        self.lcd.lcd_display_string("" + args.server, 3)

                    if players is not None:
                        if len(players) > 0:
                            self.lcd.lcd_display_string(
                                "Players count: " + str(len(players)), 4
                            )
                        else:
                            self.lcd.lcd_display_string("Player not found!", 4)
                        sleep(0.1)
                    else:
                        self.lcd.lcd_display_string("No player", 4)
                else:
                    self.lcd.lcd_display_string(today.strftime("%d/%m/%Y %H:%M"), 1)
                    self.lcd.lcd_display_string("LMS not connected on", 2)
                    self.lcd.lcd_display_string(args.server, 3)
                    self.lcd.lcd_display_string("no player", 4)


if __name__ == "__main__":
    """
    This is the main:
    - grabbing params from CLI
    -
    """

    print("--- LMS API Requester ---")
    print("please use -h for help")
    print("Enjoy using LMS!")

    description = "LMS API Requester"
    server_help = "ip and port for the server. something like 192.168.1.192:9000"
    lcd_help = "LCD address something like 0x3f"
    i2c_help = "i2cdetect port, 0 or 1, 0 for Orange Pi Zero, 1 for Rasp > V2"
    display_mode_help = "set to volume or bitrate"
    player_name_help = "player name to lock the LCD on it"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-s", "--server", type=str, default="192.168.1.192:9000", help=server_help
    )
    parser.add_argument(
        "-l", "--lcd", type=lambda x: int(x, 0), default=0x3F, help=lcd_help
    )
    parser.add_argument("-i", "--i2c_port", type=int, default=1, help=i2c_help)
    parser.add_argument("-v", "--virtual_lcd", type=str, default="no", help=lcd_help)
    parser.add_argument(
        "-d", "--display_mode", type=str, default="", help=display_mode_help
    )
    parser.add_argument(
        "-p", "--player_name", type=str, default="", help=player_name_help
    )

    args = parser.parse_args()

    # we are supposed to run this to the end of time
    while True:
        myLCD = LCD20(
            args.server,
            args.lcd,
            args.i2c_port,
            args.virtual_lcd,
            args.display_mode,
            args.player_name,
        )
        try:
            myLCD.main_loop()
        except Exception as err:
            print(str(err))
            myLCD = None
