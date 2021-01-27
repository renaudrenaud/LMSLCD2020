"""
A test for the I2C LCD
RC 2020-01-15
"""


import lcddriver
from datetime import datetime
from time import sleep
 
lcd = lcddriver.lcd()
lcd.lcd_clear()
 
while True:
    today = datetime.today()
    lcd.lcd_display_string(today.strftime("%d/%m/%Y"), 1)
    lcd.lcd_display_string(today.strftime("%H:%M:%S"), 2)
    sleep(.8)
