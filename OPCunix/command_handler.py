import os
import serial_manager
from collections import defaultdict
import weakref
import datetime
import subprocess
import signal


def process(comm):
    """
    A function to split and process a command from the program
    :param comm: Everything on the command line before \n, options delimited by spaces
    :return: exit status, 0 if close program
    """
    comm_arr = comm.split()

    if comm_arr[0] == "list":
        if comm_arr[1] == "ports":
            port_list()
        if comm_arr[1] == "ucass":
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
        if comm_arr[1] == "delete":
            delete_ucass(comm_arr)
        return 1

    else:
        print "Invalid Selection"
        return 1


def make_title():
    os.system('clear')
    print("\t**************************************************")
    print("\t*****    UCASS Interface Software (Linux)    *****")
    print("\t**************************************************")


def port_list():
    ports = serial_manager.list_ports()
    print ports


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

    def __delete__(self, instance):
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

