"""
This class to manage bus communication for the LCD
We cannot raise an error when init
the way to raise an error is to write 

"""


from time import sleep

import smbus2


class i2c_device:
    def __init__(self, addr, port=1):
        self.addr = addr
        self.bus = smbus2.SMBus(port)

    def write_cmd(self, cmd):
        """
        write a single command

        """
        try:
            self.bus.write_byte(self.addr, cmd)
            sleep(0.0001)
        except Exception as err:
            raise TypeError("LCD_Write >" + str(err))

    def write_cmd_arg(self, cmd, data):
        """
        write a command and argument

        """
        self.bus.write_byte_data(self.addr, cmd, data)
        sleep(0.0001)

    def write_block_data(self, cmd, data):
        """
        Write a block of data
        """
        self.bus.write_block_data(self.addr, cmd, data)
        sleep(0.0001)

    def read(self):
        # Read a single byte
        return self.bus.read_byte(self.addr)

    def read_data(self, cmd):
        # Read
        return self.bus.read_byte_data(self.addr, cmd)

    def read_block_data(self, cmd):
        # Read a block of data
        return self.bus.read_block_data(self.addr, cmd)
