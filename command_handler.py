import os
import serial_manager


def process(comm):
    if comm == "list":
        port_list()
    elif comm == "clear":
        os.system('clear')
    else:
        print "Invalid Selection"


def make_title():
    os.system('clear')
    print("\t**************************************************")
    print("\t*****    UCASS Interface Software (Linux)    *****")
    print("\t**************************************************")


def port_list():
    ports = serial_manager.list_ports()
    print ports
