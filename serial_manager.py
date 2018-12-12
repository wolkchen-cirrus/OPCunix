import glob
import serial
import time


class OPC:

    def __init__(self, port_name, mod):
        """ Creates an instance of the 'OPC' class
            :parameter:
                port_name - Name of port i.e. /dev/tty**
                mode - Which mode is being used (PC, Logger, Arduino, etc.)
        """
        self.mode = mod
        self.port = port_name
        self.opc_port = serial.Serial()

    def init_port(self):
        """Starts communications with the OPC
            :raises:
                A name error if an invalid mode is input
        """
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
        self.opc_port.flush()
        self.opc_port.close()

    def read_hist(self):
        """ Reads 1 Line of Histogram Data From UCASS
            :returns:
                String of raw bytes to be processed into int16
        """
        self.open_port()
        if self.mode == 'COMP':
            byte_string = []
            self.command_byte(0x30)
            for i in range(43):
                time.sleep(0.00001)
                byte_in = self.opc_port.write(0x30)
                byte_string.append(byte_in)
            self.close_port()
            return byte_string
        elif self.mode == 'LOG':
            self.opc_port.read_until()
        elif self.mode == 'ARD':
            self.opc_port.read_until()

    def command_byte(self, comm):
        """ Sends a Command Byte to the OPC and Checks the Response
            :parameter:
                comm - a byte corresponding to a UCASS command
            :raises:
                A RuntimeError if the connection takes 60 seconds
        """
        ready = 0xF3
        valid = False
        timeout = 0
        while not valid:
            response = self.opc_port.write(comm)
            if response != ready:
                print ("UCASS Not Communicating, Wait 2s")
                print ("Byte Received = ", response)
                print ("Byte Expected = ", ready)
                time.sleep(2)
                timeout = timeout + 1
                if timeout > 60:
                    raise RuntimeError("Connection Timed Out, Check Hardware")
        time.sleep(0.01)


def byte_to_int(bytes_in):
    int_out = 0
    for i in bytes_in:
        int_out = int_out*256+int(i)
    return int_out


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




