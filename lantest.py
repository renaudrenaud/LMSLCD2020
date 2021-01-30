import sh    
  
for num in range(10,40):  
    ip = "192.168.1."+str(num)  
  
    try:  
        sh.ping(ip, "-c 1",_out="/dev/null")  
        print ("PING ",ip , "OK")  
    except sh.ErrorReturnCode_1:  
        pass   