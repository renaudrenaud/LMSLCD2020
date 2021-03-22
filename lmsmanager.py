"""
2020-01-25: Renaud wants to use Python3 "requests" for LMS

There was something existing but in python2 and something else than requests
The goal was to use Python3 and Request to have something more "modern"

This is just some code has a hobby and maybe an help to decypher the
LMS API.
"""

import requests
import argparse
from json import dumps

class LmsServer:
    """
    This class to grab informations from the LMS SERVER
    2021-03-20: v1.1.2: mode docstring
    2021-03-18: v1.1.1: cleaning code (todo: doc)
                            - dead method
                            - better naming
                        add methods
                            - player on / off 
                            - player sleep in x seconds
                            - player skip track (positive or neg to scroll the playlist)
                            - server is scanning
                            - server scanning status

    2021-03-10: v1.0.1: cleaning code
    2021-03-09: v1.0.0: "Official" v1 version!
    2021-01-25: v0.0.1: starting

    """
    def __init__(self, serveur_ip):
        """

        """
        self.__version__ = "1.1.2"
        self.URL = "http://" + serveur_ip + "/jsonrpc.js" 

    def _cls_execute_request(self, payload)-> dict:
        """
        Execute request

        """
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.request("POST", url=self.URL, headers=headers, data=payload)
        except Exception as err:
            print(str(err))
            return err
        return response.json()
    
    def cls_players_list(self)-> list:
        """
        Returns a list of players
        detected connected to the server

        input
        : None
        
        returns
        : players, list of dict
        
        """

        payload='{"id": 0, "params": ["-",["players","0"]],"method":"slim.request"}'

        try:
            players = self._cls_execute_request(payload)["result"]["players_loop"]
        except Exception as err:
            return err
        # for player in players:
        #    print(player["playerid"] + " =" + player["modelname"] + " - " + player["name"] + " : " + str(player["isplaying"]))
        
        return players

    
    def cls_player_on_off(self, mac_player:str, on_off:int)->None:
        """
        player on or off

        input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        : on_off: int, value between 0-1, 0=OFF, 1=ON


        returns
        : None
        """
        if on_off == 0 or on_off == 1:
            payload = '{"id": 0, "params": ["' + mac_player + '",["power","' + str(on_off) + '"]],"method": "slim.request"}'
            self._cls_execute_request(payload)
            print("Power on/off: " + str(on_off))
        else:
            print("Power on off value should be 0 or 1, received:" + str(on_off))
    
    def cls_player_sleep(self, mac_player:str, seconds_before_sleep:int)->None:
        """
        player on or off

        input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        : seconds_before_sleep: number of seconds before sleep

        returns
        : None
        """

        payload = '{"id": 0, "params": ["' + mac_player + '",["sleep","' + str(seconds_before_sleep) + '"]],"method": "slim.request"}'
        self._cls_execute_request(payload)
        print("Player goind to sleep in: " + str(seconds_before_sleep) + " seconds")
    
    def cls_player_define_volume(self, mac_player:str, volume:int)->None:
        """
        Define the volume for specified player

        input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        : volume: int, between 0-100

        returns
        : None
        """
        if volume > 100:
            volume = 100
        elif volume < 0:
            volume = 0
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["mixer","volume","' + str(volume) + '"]],"method": "slim.request"}'
        self._cls_execute_request(payload)
        print("volume set to:" + str(volume))

    
    def cls_player_play(self, mac_player:str)->None:
        """
        player play!

        input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        
        """
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["button","play"]],"method": "slim.request"}'
        self._cls_execute_request(payload)
        print("Player play:" + mac_player)
    
    def cls_player_stop(self, mac_player:str)->None:
        """
        player stop!

        input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        
        """
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["button","stop"]],"method": "slim.request"}'
        self._cls_execute_request(payload)
        print("Player stop:" + mac_player)

    def cls_player_next_previous(self, mac_player:str, skip:int)->None:
        """
        player on or off

        input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        : skip: number of track(s) to skip, ie 1, -1, 4, -2...
        """

        payload = '{"id": 0, "params": ["' + mac_player + '",["playlist","index","' + str(skip) + '"]],"method": "slim.request"}'
        self._cls_execute_request(payload)
        print("Player is skipping : " + str(skip) + " track(s)")
    
    def cls_player_status(self, mac_player:str)->dict:
        """
        player status

        input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79

        returns
        : dict: list of information about the player
        
        """
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["status"]],"method": "slim.request"}'
        player_status = self._cls_execute_request(payload)
        # for status in player_status["result"]:
        #    print(status + ":" + str(player_status["result"][status]))

        return player_status["result"]

    def cls_player_current_title_status(self, mac_player:str)->dict:
        """
        player status

        input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79

        returns
        : dict: list of information about the player
        
        """
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["status","current_title"]],"method": "slim.request"}'
        player_status = self._cls_execute_request(payload)

        try:
            return player_status["result"]
        except:
            return None
    
    def cls_song_info(self, song_id, player_id):
        """
        Grab info about song

        input
        : song_id; int
        : palyer_id: str as a MAC address, ie : "00:11:22:33:44:55:66"

        returns
        : dict containing info
        """
        
        payload = '{"id": 0,"params": ["' + player_id + '",["songinfo",0,100,"track_id:' + str(song_id) + '"]],"method": "slim.request"}'

        song_info = self._cls_execute_request(payload)
        return song_info["result"]

    def cls_server_status(self)->dict:
        """
        grab the server status

        """
        payload = '{"id": 0,"params": ["-",["serverstatus",0,100]],"method": "slim.request"}'
        server_status = self._cls_execute_request(payload)
        
        return server_status # ["result"]

    def cls_server_is_scanning(self)->bool:
        """
        returns:
        : True if scanning
        : False otherwise
        """
        payload = '{"id": 0, "params": ["00:00:00:00:00",["rescanprogress"]],"method": "slim.request"}'
        rescan = self._cls_execute_request(payload)
        # print("Server is scanning? " + str(rescan["result"]))
        if rescan["result"]["rescan"]== 1:
            # print(True)
            return True
        else:
            # print(False)
            return False

    def cls_server_scanning_status(self)->dict:
        """
        check the server to know the scan status
        and returns the scan status

        returns
        : rescan["result"] dict if scanning, ie
            {'discovering_directory': -1,
                'fullname': 'Discovering files/di...o/Musiques', 
                'info': '/mnt/syno/Musiques/J...and I.flac',
                'rescan': 1, 
                'steps': 'discovering_directory',
                'totaltime': '00:00:30'}
        if not scanning: {'rescan': 0}  
        """
        
        payload = '{"id": 0, "params": ["00:00:00:00:00",["rescanprogress"]],"method": "slim.request"}'
        rescan = self._cls_execute_request(payload)
        # print("Server scanning status " + str(rescan["result"]))
        return rescan["result"]


if __name__ == "__main__":

    print("--- LMS API Requester ---")
    print("please use -s option to define your IP:PORT address")
    print("ie: python lmsmanager.py -s 192.168.1.112:9000")
    print("note: at least one player shoud be playing for demoing!")

    description = "LMS API Requester"
    server_help = "ip and port for the server. something like 192.168.1.192:9000"
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument("-s","--server", type=str, default="192.168.1.192:9000", help = server_help)

    args = parser.parse_args()
    myServer = LmsServer(args.server)

    myServer.cls_server_is_scanning()
    myServer.cls_server_scanning_status()

    players = myServer.cls_players_list()
    
    for player in players:
        if player["isplaying"] == 1:
            print("Waoo ->" + player['name'])
            # define volume
            myServer.cls_player_define_volume(player['playerid'], 40)
            
            # next previous track
            myServer.cls_player_next_previous(player['playerid'], 1)
            myServer.cls_player_next_previous(player['playerid'],-1)

            # stop and play
            myServer.cls_player_stop(player['playerid'])
            myServer.cls_player_play(player['playerid'])
            
            # Off / On
            myServer.cls_player_on_off(player['playerid'], 0)
            myServer.cls_player_on_off(player['playerid'], 1)
            
            # Sleep in 1000 seconds
            myServer.cls_player_sleep(player['playerid'], 1000)

            myServer.cls_player_status(player['playerid'])
            song = myServer.cls_player_current_title_status(player['playerid'])
            print(str(song))
            break

