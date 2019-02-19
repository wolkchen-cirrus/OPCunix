import os
from collections import defaultdict
import weakref
import subprocess
import signal
import serial
import glob
import serial_manager
import sys


used_ports = []


def process(comm):
    """
    A function to split and process a command from the program
    :param comm: Everything on the command line before \n, options delimited by spaces
    :return: exit status, 0 if close program
    """
    comm_arr = comm.split()

    if not comm_arr:
        return 1

    if comm_arr[0] == "list":
        if comm_arr[1] == "ports":
            print list_ports()
        elif comm_arr[1] == "ucass":
            get_ucass_list()
        return 1

    elif comm_arr[0] == "clear":
        os.system('clear')
        make_title()
        return 1

    elif comm_arr[0] == "exit":
        return 0

    elif comm_arr[0] == "ucass":
        if comm_arr[1] == "init":
            InitUCASS(comm_arr)
        elif comm_arr[1] == "delete":
            delete_ucass(comm_arr)
        elif comm_arr[1] == "config":
            read_config(comm_arr)
        return 1

    else:
        print "Invalid Selection"
        return 1


def make_title():
    os.system('clear')
    print("\t**************************************************")
    print("\t*****    UCASS Interface Software (Linux)    *****")
    print("\t**************************************************")


class KeepRefs(object):
    __refs__ = defaultdict(list)

    def __init__(self):
        self.__refs__[self.__class__].append(weakref.ref(self))

    @classmethod
    def get_instances(cls):
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                yield inst


class InitUCASS(KeepRefs):
    def __init__(self, comm_arr):
        super(InitUCASS, self).__init__()
        module_path = os.path.dirname(os.path.realpath(__file__))
        settings_path = module_path + "/ucass_settings.txt"
        process_path = module_path + "/ucass_subprocess.py"
        process_path = 'python' + ' ' + process_path
        self.settings = open(settings_path, "w")
        self.settings.write(' '.join(comm_arr))
        self.settings.close()
        self.process = subprocess.Popen(['konsole', '-e', '$SHELL', '-c', process_path])
        self.name = process_opts(comm_arr, '-n')
        self.port = process_opts(comm_arr, '-p')
        used_ports.append(self.port)

    def __delete__(self, instance):
        used_ports.remove(self.port)
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        print('Deleted UCASS With Designation: %d' % self.name)


def get_ucass_list():
    names = []
    ports = []
    for i in InitUCASS.get_instances():
        names.append(i.name)
        ports.append(i.port)
    print("\tDesignation:\tOn Port:")
    for i in range(len(names)):
        string = "\t".join([names[i], ports[i]])
        string = "\t" + string
        print(string)


def delete_ucass(comm_arr):
    name = process_opts(comm_arr, '-n')
    for i in InitUCASS.get_instances():
        if i.name == name:
            i.__delete__()


def process_opts(comm_arr, look_for):
    size = len(comm_arr)
    for i in range(size):
        if comm_arr[i] == look_for:
            return comm_arr[i+1]
    return []


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


def read_config(comm_arr):
    """
    A function to read the config vars from a ucass on a port
    :param comm_arr: The command array entered, only uses -p
    """
    port = process_opts(comm_arr, '-p')
    used = 1
    try:
        used_ports.index(port)
    except ValueError:
        used = 0
        pass
    if used == 1:
        print("Serial port in use with name: %d" % port)
    else:
        ucass = serial_manager.OPC(port)
        ucass.read_info_string()
        ucass.read_config_vars()
        print(ucass.info_string)
        print("bb0\tbb1\tbb2\tbb3\tbb4\tbb5\tbb6\tbb7\tbb8\tbb9\tbb10\tbb11\tbb12\tbb13\tbb14\tbb15\tGSC\tID")
        bb_str = "\t".join(str(i) for i in ucass.bbs)
        bb_str = bb_str.replace('[', '')
        bb_str = bb_str.replace(']', '')
        sys.stdout.write(bb_str)
        sys.stdout.write('\t')
        gsc = str(ucass.gsc)
        gsc = gsc.replace('(', '')
        gsc = gsc.replace(')', '')
        gsc = gsc.replace(',', '')
        sys.stdout.write(gsc)
        sys.stdout.write('\t')
        print(str(ucass.id))
