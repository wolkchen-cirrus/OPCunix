import glob


class OPC:

    def __init__(self, portname, mode):

        if mode == 'COMP':
            baud = 9600
            parityB = 0
            dataB = 8
            stopB = 1
        elif mode == 'LOG':
            baud = 9600
            parityB = 0
            dataB = 8
            stopB = 1
        elif mode == 'ARD':
            baud = 9600
            parityB = 0
            dataB = 8
            stopB = 1
        else:
            NameError

    def list_ports(self):
        """ Gets Serial Port Names (**nix only)
            :returns:
                A list of serial ports currently available
        """
        ports = glob.glob('/dev/tty[a-zA-Z]*')
        return ports


print(OPC.list_ports())
