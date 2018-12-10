import serial
import glob

def list_ports():
    """ Gets Serial Port Names (**nix only)
        :returns:
            A list of serial ports currently available
    """
    ports = glob.glob('/dev/tty[A-Za-Z]*')
    ports_out = []
    for i in ports:
        try:
            port = serial.Serial(i)
            port.close()
            ports_out.append(i)
        except (OSError, serial.SerialException):
            pass
    return ports_out







