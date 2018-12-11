import glob
import serial


class OPC:

    def __init__(self, port_name, mod):
        """ Starts Communication With OPC on a Serial Port
            :parameter:
                port_name - Name of port i.e. /dev/tty**
                mode - Which mode is being used (PC, Logger, Arduino, etc.)
            :returns:
                A serial port object from pyserial library
        """
        self.mode = mod
        self.port = port_name
        self.opc_port = serial.Serial()

    def init_port(self):
        if self.mode == 'COMP':
            baud = 9600
            parity_b = 0
            data_b = 8
            stop_b = 1
        elif self.mode == 'LOG':
            baud = 9600
            parity_b = 0
            data_b = 8
            stop_b = 1
        elif self.mode == 'ARD':
            baud = 9600
            parity_b = 0
            data_b = 8
            stop_b = 1
        else:
            raise NameError('Invalid Mode')

        self.opc_port = serial.Serial(self.port, baud, data_b, parity_b, stop_b)

    def open_port(self):
        self.opc_port.open()

    def close_port(self):
        self.opc_port.close()

    def read_hist(self):
        if self.mode == 'COMP':
            self.opc_port.read_until()
        elif self.mode == 'LOG':
            self.opc_port.read_until()
        elif self.mode == 'ARD':
            self.opc_port.read_until()


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


print(list_ports())
