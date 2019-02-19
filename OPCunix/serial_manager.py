import glob
from time import sleep
from usbiss import spi
import struct
import serial


class OPC(object):

    def __init__(self, port_name):
        """ Creates an instance of the 'OPC' class
            :parameter:
                port_name - Name of port i.e. /dev/tty**
                mode - Which mode is being used (PC, Logger, Arduino, etc.)
        """
        self.port = port_name
        self.opc_port = spi.SPI(port_name, mode=1, max_speed_hz=500000)

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
        self.command_byte([0x30])
        self.hist = []
        self.mtof = []
        raw = []
        index = 0
        for i in range(43):
            sleep(0.00001)
            buf = self.opc_port.xfer([0x06])[0]
            raw.append(buf)
        for i in range(16):
            self.hist.append(byte_to_int16(raw[i*2], raw[i*2+1]))
            index = index+2
        for i in range(4):
            self.mtof.append(raw[index])
            index = index+1
        self.period = byte_to_int16(raw[36], raw[37])
        self.checksum = byte_to_int16(raw[38], raw[39])
        self.reject_glitch = raw[40]
        self.reject_ltof = raw[41]
        self.reject_ratio = raw[42]

    def read_info_string(self):
        self.command_byte([0x3F])
        for i in range(60):
            sleep(0.00001)
            buf = self.opc_port.xfer([0x06])[0]
            self.info_string += chr(buf)

    def read_config_vars(self):
        self.command_byte([0x3C])
        self.bbs = []
        raw = []
        for i in range(38):
            sleep(0.00001)
            buf = self.opc_port.xfer([0x06])[0]
            raw.append(buf)
        for i in range(16):
            self.bbs.append(byte_to_int16(raw[i*2], raw[i*2+1]))
        self.gsc = byte_to_float(raw[32], raw[33], raw[34], raw[35])
        self.id = raw[37]

    def command_byte(self, command):
        self.opc_port.xfer(command)
        sleep(0.01)

    def close(self):
        self.opc_port.close()


def byte_to_int16(lsb, msb):
    return (msb << 8) | lsb


def byte_to_float(b1, b2, b3, b4):
    arr = bytearray([b1, b2, b3, b4])
    return struct.unpack('<f', arr)


def list_ports():
    """ Gets Serial Port Names (**nix only)
        :returns:
            A list of serial ports currently available
    """
    ports = glob.glob('/dev/tty[a-zA-Z]*')
    port_list = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            port_list.append(port)
        except (OSError, serial.SerialException):
            pass

    return port_list
