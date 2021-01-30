"""
LCD driver.

- Do not forget to instantiate with the address value using sudo i2cdetect -y 1
 
"""
from time import sleep

class lcd:
   #initializes objects and lcd
   def __init__(self, address:int = 0x3f) -> None:
      """
      Input
      - address: int, the LCD address in hex format, grabbed by sudo i2cdetect -y 1, ie 0x3f or 0x27...

      Ouput
      - None
      """
      print("No lcd driver initialized!")
      self.string1 = ""
      self.string2 = ""
      sleep(0.2)

   def lcd_display_string(self, string, line):
      
      if line == 1:
         self.string1 = (string + " " * 16)[:16]
      else:
         self.string2 = (string + " " * 16)[:16]

      print( "\r", self.string1 + " --- " + self.string2, end="")

   # clear lcd and set to home
   def lcd_clear(self):
      print('clear screen')
      # self.lcd_write(LCD_CLEARDISPLAY)
      # self.lcd_write(LCD_RETURNHOME)