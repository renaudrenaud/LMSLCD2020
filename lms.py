"""
import requests

server = "http://192.168.1.192:9000/jsonrpc.js"

myDataPing = {"id":1, "method": "slim.request", "params":"ping"}
cmd = ["-",["player count ?",["_count"]]]
myDataCountPlayers = {"id":1, "method": "slim.request", "params":cmd}   


headers = {'Content-Type':'application/json'}

player = '-'
params = "ping"
cmd = ["-",["player count ?",["_count"]]]
# cmd = [player, params]

{"id":0,"method":"slim.request","params":["-",["player count ?"]]}

data = {"id": 1, "method": "slim.request", "params": cmd}

try:
    r = requests.post(server, headers = headers, data = data)
    print(r.response.status_code)
    
except Exception as err:
    print(err)


print("finshed")
"""

import requests

url = "http://192.168.1.192:9000/jsonrpc.js"

payload='{"id":0,"params": ["08:57:00:b7:c9:21",["button","pause"]],"method":"slim.request"}'
payload='{"id":0,"params": ["player count?"],"method":"slim.request"}'

headers = {'Content-Type': 'application/json'}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)