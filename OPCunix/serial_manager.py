from time import sleep
from usbiss import spi
import struct


class OPC(object):

    def __init__(self, port_name):
        """
        Creates an instance of the 'OPC' class
        :param port_name: Name of port i.e. /dev/tty**
        """
        self.port = port_name       # Define the port and open using the usbiss.spi module
        self.opc_port = spi.SPI(port_name, mode=1, max_speed_hz=500000)

        # The following variables are used to store UCASS data, and written to by other functions in the class.
        self.info_string = ""
        self.bbs = []
        self.hist = []
        self.mtof = []
        self.period = 0
        self.gsc = 0
        self.id = 0
        self.checksum = 0
        self.reject_glitch = 0
        self.reject_ratio = 0
        self.reject_ltof = 0

    def read_histogram_data(self):
        """
        This function sends the SPI commands for reading the UCASS histogram, i.e. the number of counts in each bin
        after the last time the histogram was read (or reset)
        """
        self.command_byte([0x30])                                   # 0x30 is the byte which starts hist data transfer
        self.hist = []                                              # Appended-to variables are emptied first
        self.mtof = []
        raw = []                                                    # Raw data storage
        index = 0                                                   # Index keeps track of where vars are in raw[]
        for i in range(43):                                         # Fill the raw buffer (43 bytes long)
            sleep(0.00001)                                          # Wait 10us
            buf = self.opc_port.xfer([0x06])[0]
            raw.append(buf)
        for i in range(16):                                         # 0-31 (32 bytes) contain counts data
            self.hist.append(byte_to_int16(raw[i*2], raw[i*2+1]))   # 15 bins, each is 2 bytes and is processed as such
            index = index+2                                         # Step by 2 since each iteration records 2 bytes
        for i in range(4):                                          # MToFs are 1 byte (4 of)
            self.mtof.append(raw[index])
            index = index+1                                         # Step index by 1
        self.period = byte_to_int16(raw[36], raw[37])               # int16 for period
        self.checksum = byte_to_int16(raw[38], raw[39])             # int16 for checksum
        self.reject_glitch = raw[40]                                # 1 byte for the reject flags
        self.reject_ltof = raw[41]
        self.reject_ratio = raw[42]

    def read_info_string(self):
        """
        A function to read the info string from the UCASS, which contains the firmware version and other data.
        """
        self.info_string = ""                       # Clean previous assignments
        self.command_byte([0x3F])                   # 0x3F is the command for the info string
        for i in range(60):                         # info string is a simple char string, 60 bytes long
            sleep(0.00001)                          # Wait for 10us
            buf = self.opc_port.xfer([0x06])[0]
            self.info_string += chr(buf)            # Simply append the char to the buf

    def read_config_vars(self):
        """
        A function to read the configuration variables from the UCASS. This is the bin boundaries, the gain scaling
        coefficient, and the ID number.
        """
        self.command_byte([0x3C])                                       # 0x3C is the command for config vars
        self.bbs = []                                                   # Clear appended-to variables
        raw = []
        for i in range(38):                                             # Config vars buffer is 38 bytes long
            sleep(0.00001)                                              # Wait for 10us
            buf = self.opc_port.xfer([0x06])[0]
            raw.append(buf)
        for i in range(16):                                             # 16 bin boundaries (int16), 32 bytes
            self.bbs.append(byte_to_int16(raw[i*2], raw[i*2+1]))
        self.gsc = byte_to_float(raw[32], raw[33], raw[34], raw[35])    # GSC is a float (largely unused)
        self.id = raw[37]                                               # ID is one byte

    def command_byte(self, command):
        """
        A function to send a command byte to the UCASS, causing it to send data
        :param command: The hexadecimal byte that tells the UCASS which data to send
        """
        self.opc_port.xfer(command)     # Transfer the command
        sleep(0.01)                     # Wait 10ms

    def close(self):
        """
        Simple function to close the ucass and shut down the spi.SPI object
        """
        self.opc_port.close()


def byte_to_int16(lsb, msb):
    """
    Converts two bytes (lsb, msb) to an int16
    :param lsb: Least significant bit
    :param msb: Most significant bit
    :return: the 16 bit integer from the two bytes
    """
    return (msb << 8) | lsb


def byte_to_float(b1, b2, b3, b4):
    """
    A function to get a 32 bit float from 4 bytes read in order [b1, b2, b3, b4]
    :param b1: first byte
    :param b2: second byte
    :param b3: third byte
    :param b4: fourth byte
    :return: the byte array from b1, b2, b3, b4 unpacked as a float using the 'struct' module
    """
    arr = bytearray([b1, b2, b3, b4])
    return struct.unpack('<f', arr)
