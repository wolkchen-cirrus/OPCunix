import os
from collections import defaultdict
import weakref
import datetime
import subprocess
import signal
import serial
import glob
import serial_manager


used_ports = []


def process(comm):
    """
    A function to split and process a command from the program
    :param comm: Everything on the command line before \n, options delimited by spaces
    :return: exit status, 0 if close program
    """
    comm_arr = comm.split()

    if comm_arr[0] == "list":
        if comm_arr[1] == "ports":
            list_ports()
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
        self.settings = open("ucass_settings.txt", "w")
        self.settings.write(comm_arr)
        self.settings.close()
        self.process = subprocess.Popen(['konsole', '-e', '$SHELL', '-c', 'python ucass_subprocess.py'])
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
    for i in comm_arr:
        if comm_arr[i] == look_for:
            return comm_arr[i+1]
        else:
            return []


def get_base_name(comm_arr):
    name = process_opts(comm_arr, '-n')
    date_time = str(datetime.datetime.now())
    date_time = date_time.replace(' ', '_')
    base_name = "UCASS_"
    base_name += name
    base_name += "_"
    base_name += date_time
    return base_name


def make_log(comm_arr):
    base_name = get_base_name(comm_arr)
    path_file = open("default_path.txt", "r")
    path = path_file.read()
    base_name += "_00.csv"
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    path_name = path
    for i in range(100):
        path_name = path
        name_l = list(base_name)
        name_l[-1 - 5] = str(int(i / 10))
        name_l[-1 - 4] = str(int(i % 10))
        name = "".join(name_l)
        path_name += '/'
        path_name += name
        if os.path.exists(path_name) is False:
            break
    return path_name


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
        print('\n')
        print("bb0,bb1,bb2,bb3,bb4,bb5,bb6,bb7,bb8,bb9,bb10,bb11,bb12,bb13,bb14,bb15,GSC,ID\n")
        bb_str = "\t".join(str(i) for i in ucass.bbs)
        bb_str = bb_str.replace('[', '')
        bb_str = bb_str.replace(']', '')
        print(bb_str)
        print('\t')
        print(str(ucass.gsc))
        print('\t')
        print(str(ucass.id))
        print('\n')
