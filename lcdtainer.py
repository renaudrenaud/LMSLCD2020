import os

from testLCD import LCD16


LCD_ADDRESS = int(os.environ.get("LCD", 0x3f), 16) 
I2C_PORT = int(os.environ.get("I2C_PORT",1))
VIRTUAL_LCD = False

if os.environ.get("VIRTUAL_LCD")in ["TRUE","True","true"]:
    VIRTUAL_LCD = True

while True:
    myLCD = LCD16(os.environ.get("LMS_SERVER","192.168.1.120"),
                    LCD_ADDRESS,
                    I2C_PORT,
                    VIRTUAL_LCD,
                    os.environ.get("DISPLAY_MODE","volume"),
                    os.environ.get("PLAYER_NAME",""))
    try:
        myLCD.main_loop()
    except Exception as err:
        print(str(err))
        myLCD = None 