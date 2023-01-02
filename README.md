# LMSLCD2020
Logitech Media Server to LCD, use API Python 3 and Request

## Why this code
I wanted something to use a LCD 20x4 to show information from the Logitech Media Server.

I also wanted some things in the project:
* use python 3
* use request
* use json /API from the Logitech Media Server


## ENV variables Since january 2023 v2.4

Environment variables are now used.

* **LMS_SERVER** to define the server with the port, ie: 192.168.1.120:9000
* **LMS_LCD** to define the address for the LCD, ie 0x3F
* **LMS_I2C_PORT** to define the I2C port, dependign on the SBC coulb be 0, 1, 2... To find it use sudo i2cdetect -y "x"
* **LMS_VIRTUAL_PORT** indicates you do not want to use some LCD, instead it prints on the screen
* **LMS_DISPLAY_MODE** to define what to print on the LCD : "" or "cpu" or "clock" or "volume"
* **LMS_PLAYER_NAME** to lock the LCD on a specific player

**Note** you can still use the old parameters :



## I have 2 lines 16 char LCD

Congratulations! run the script testLCD.py
* -i for the i2c port, ie: 0 for old Raspberry or Orange Pi Zero, 1 for new Raspberry (with 40 GPIO pins), 3 for the Orange Pi Zero 2
* -l for the LCD address grabbed with i2cdetect
* -d for diplay "volume", usefull for the 16x2
* -p for player, indicating your LCD must stay on the same player, if not, LCD shows the current playing player
* -s for server, indicates the LMS SERVER ip adress, ie: **192.168.1.192:9000** assuming port is 9000 

## Seeems LCD is not ok

Please check the bus. Depending on your card, you have to use -y value as 0, 1, 2, 3... With the following command:

sudo i2cdetect -y 0

* Orange Pi Zero or Zero LTS or old Raspberries with 26 GPIO: -y 0
* Raspberry with 40 GPIO: -y 1
* Orange Pi Zero 2: -y 3


Example for Orange Pi Zero 2
python3 /home/orangepi/sources/LMSLCD2020-main/testLCD.py -i 3 -l 0x27 -d volume -p OPZ2_SU8

## Ho No: I have a 4 lines 20 chars!
No problem, use the same syntax, changing the script name

python3 /home/orangepi/sources/LMSLCD2020-main/lcd20.py -i 3 -l 0x27 -d volume -p OPZ2_SU8
