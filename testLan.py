# sudo apt install net-tools

import os
import socket
devices = []
for device in os.popen('arp -a'): 
    # print(device)
    devices.append(device)
    ip = (device.split(')'))[0].split('(')[1]
    print(ip)
    try:
        print(socket.gethostbyaddr(ip))
    except:
        pass