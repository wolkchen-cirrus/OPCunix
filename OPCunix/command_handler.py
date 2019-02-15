import os
import serial_manager


def process(comm):
    if comm == "list":
        port_list()
        return 1
    elif comm == "clear":
        os.system('clear')
        make_title()
        return 1
    elif comm == "exit":
        return 0
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
