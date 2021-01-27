"""
2020-01-25: Renaud Coustellier Wants some Python3 requests for LMS
"""

import requests
import argparse

class LMS_SERVER:
    """
    This class tp grab informations from the LMS SERVER
    
    2020-01-25: 0.0.1 : starting

    """
    def __init__(self, serveur_ip):
        """

        """
        self.__version__ = "0.0.1"
        self.URL = "http://" + serveur_ip + "/jsonrpc.js" 

    def cls_execute_request(self, payload)-> dict:
        """
        Execute request
        """
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.request("POST", url=self.URL, headers=headers, data=payload)
        except Exception as err:
            print(str(err))
        
        # print(response.text)
        return response.json()
    
    def _cls_build_players_list(self)-> list:

        payload='{"id": 0, "params": ["-",["players","1"]],"method":"slim.request"}'

        players = self.cls_execute_request(payload)["result"]["players_loop"]

        for player in players:
            print(player["playerid"] + " =" + player["modelname"] + " - " + player["name"] + " : " + str(player["isplaying"]))
        
        return players

    def cls_define_volume(self, mac_player:str, volume:int)->None:
        """
        Define the volume for specified player

        Input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        : volume: int, between 0-100
        """
        if volume > 100:
            volume = 100
        elif volume < 0:
            volume = 0
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["mixer","volume","' + str(volume) + '"]],"method": "slim.request"}'
        self.cls_execute_request(payload)
        print("volume set to:" + str(volume))

    
    def cls_player_play(self, mac_player:str)->None:
        """
        player play!

        Input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        
        """
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["button","play"]],"method": "slim.request"}'
        self.cls_execute_request(payload)
        print("Player play:" + mac_player)
    
    def cls_player_stop(self, mac_player:str)->None:
        """
        player stop!

        Input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79
        
        """
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["button","stop"]],"method": "slim.request"}'
        self.cls_execute_request(payload)
        print("Player stop:" + mac_player)

    def cls_player_status(self, mac_player:str)->dict:
        """
        player status

        Input
        : mac_player: str, the player mac address, ie: 5a:65:a2:33:80:79

        Output
        : dict: list of information about the player
        
        """
        
        payload = '{"id": 0, "params": ["' + mac_player + '",["status"]],"method": "slim.request"}'
        player_status = self.cls_execute_request(payload)
        for status in player_status["result"]:
            print(status + ":" + str(player_status["result"][status]))

        return player_status["result"]
    
    def _cls_count_players(self)-> int:
        """
        try to count players
        """
        payload='{"id": 0, "params": ["-",["players","1"]],"method":"slim.request"}'

        count_players = self.cls_execute_request(payload)["result"]["count"]
        print("players count:" + str(count_players))
        
        return count_players


if __name__ == "__main__":
    description = "LMS API Requester"
    server_help = "ip and port for the server. something like 192.168.1.192:9000"
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument("-s","--server", type=str, default="192.168.1.192:9000", help = server_help)

    args = parser.parse_args()

    myServer = LMS_SERVER(args.server)

    myServer._cls_build_players_list()
    myServer.cls_define_volume("5a:65:a2:aa:80:79", 60)
    # myServer.cls_player_stop("5a:65:a2:aa:80:79")
    # myServer.cls_player_play("5a:65:a2:aa:80:79")
    myServer.cls_player_status("5a:65:a2:aa:80:79")

