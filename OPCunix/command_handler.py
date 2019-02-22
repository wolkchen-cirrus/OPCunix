import os
import subprocess
import signal
import serial
import glob
import serial_manager
import sys


ucass_list = {}         # This dictionary stores the ports associated with UCASS names (user specified)
ucass_store = {}        # This dictionary stores the actual subprocess objects. Used for getting, setting, and deleting


def process(comm):
    """
    A function to split and process a command from the program
    :param comm: Everything on the command line before \n, options delimited by spaces
    :return 0: If close program
    :return 1: If continue
    """
    comm_arr = comm.split()                 # Delimit the command by spaces for options

    if not comm_arr:                        # Make sure program does not crash if no command is specified
        return 1

    if comm_arr[0] == "list":               # Primary command 'list' is for listing various attributes
        if comm_arr[1] == "ports":          # Secondary command 'ports' will specify listing serial ports
            print list_ports()
        elif comm_arr[1] == "ucass":        # Secondary command 'ucass' will specify listing instantiated ucass units
            get_ucass_list()
        return 1

    elif comm_arr[0] == "clear":            # Simply clears the screen and makes the title
        os.system('clear')
        make_title()
        return 1

    elif comm_arr[0] == "exit":             # Exits the program
        return 0

    elif comm_arr[0] == "ucass":            # Most important primary command, spawns several ucass functions
        if comm_arr[1] == "init":           # Starts a UCASS histogram subprocess, and adds to the UCASS lists
            init_ucass(comm_arr)
        elif comm_arr[1] == "del":          # Deletes a UCASS with a name specified with the '-n' option
            delete_ucass(comm_arr)
        elif comm_arr[1] == "conf":         # Tells a UCASS to list the config vars in the master process
            read_config(comm_arr)
        else:
            print "Invalid Selection"
        return 1

    else:
        print "Invalid Selection"           # Makes sure the user is aware of typos
        return 1


def make_title():
    """
    Simple function that makes a title and clears the screen
    """
    os.system('clear')
    print("\t**************************************************")
    print("\t*****    UCASS Interface Software (Linux)    *****")
    print("\t**************************************************")


class HistSubprocess(object):
    """
    An object used to describe the subprocess which handles the histogram data commands. Launches the
    'ucass_subprocess.py' file.
    :param comm_arr: The command array, usually passed by init_ucass
    """
    def __init__(self, comm_arr):
        self.name = process_opts(comm_arr, '-n')                        # User specified name
        self.port = process_opts(comm_arr, '-p')                        # User specified port
        ucass_list[self.name] = self.port                               # Adding port name to dictionary

        # Making the command path, since the ucass_subprocess is in the module directory it must be found with os first
        # for portability. Path to settings and subprocess must both be specified.
        module_path = os.path.dirname(os.path.realpath(__file__))
        settings_path = module_path + "/ucass_settings.txt"
        process_path = module_path + "/ucass_subprocess.py"
        process_path = 'python' + ' ' + process_path

        # Since the command needs to be processed by the subprocess, it needs to be transferred between the two. This is
        # done here by writing the command line to a text file, then reading it in the subprocess.
        self.settings = open(settings_path, "w")
        self.settings.write(' '.join(comm_arr))
        self.settings.close()

        # Opens the subprocess. Note the command (in square brackets) is different depending on the desktop client (i.e.
        # gnome, kde, etc.). The 'preexec_fn=os.setpgrp' is to assign the master process to a group, which allows the
        # process to be deleted easily in the 'delete_ucass' function. The type of terminal being opened will depend on
        # the desktop session, this is therefore obtained first using os. kde (plasma) and gnome are the most popular
        # terminals, but many systems are alto compatible with xterm, this is in the else statement
        self.desktop = os.environ.get('DESKTOP_SESSION')
        if 'kde' in self.desktop:
            self.process = subprocess.Popen(['konsole', '-e', '$SHELL', '-c', "exec " + process_path],
                                            preexec_fn=os.setpgrp)
        elif 'gnome' in self.desktop:
            self.process = subprocess.Popen(['gnome-terminal', '-x', "exec " + process_path], preexec_fn=os.setpgrp)
        else:
            self.process = subprocess.Popen(['xterm', '-e', "exec " + process_path], preexec_fn=os.setpgrp)


def init_ucass(comm_arr):
    """
    A function which instantiates the class the controls the histogram processing.
    :param comm_arr: The command array
    :return []: If either the name or port is unspecified
    """
    name = process_opts(comm_arr, '-n')             # User defined UCASS name
    port = process_opts(comm_arr, '-p')             # User defined UCASS port
    if not name:
        print "Name not specified, use -n"
        return                                      # Just return if no name (after user feedback)
    if not port:
        print "Port not specified, use -p"
        return                                      # Just return if no port (after user feedback)
    ucass_store[name] = HistSubprocess(comm_arr)    # Start the histogram subprocess and store in dictionary


def get_ucass_list():
    """
    This function will essentially print out the 'ucass_list' dictionary
    """
    names = []                                                  # Pre-assigning a name list
    ports = []                                                  # Pre-assigning a ports list
    for i in ucass_list.keys():                                 # Getting the list of keys (names)
        names.append(i)
    for i in ucass_list.values():                               # Getting the list of values (ports)
        ports.append(i)
    print("\tName:\tPort:")                                     # Printing a header
    for i in range(len(names)):                                 # Printing names and ports delimited by '\t'
        string = "\t".join([str(names[i]), str(ports[i])])
        string = "\t" + string
        print(string)


def delete_ucass(comm_arr):
    """
    A function which stops the histogram subprocess and removes a named UCASS from the dictionaries
    :param comm_arr: The command array
    :return []: in the case of exceptions or the name is unspecified
    :except AttributeError: If the specified name does not match a UCASS unit
    """
    name = process_opts(comm_arr, '-n')                                 # Getting name from options
    if not name:                                                        # Checking if a name is specified
        print "Name not specified"
        return
    ucass = ucass_store.get(name)                                       # Getting the HistSubprocess object
    try:
        os.killpg(os.getpgid(ucass.process.pid), signal.SIGTERM)        # Kill the subprocess
    except AttributeError:                                              # Raised if the process does not exist
        print("UCASS with designation \"%s\" does not exist" % name)    # User feedback
        return
    print('Deleted UCASS With Designation: %s' % ucass.name)            # User feedback
    del ucass_list[name]                                                # Delete the name and port from the list
    del ucass_store[name]                                               # Delete the subprocess object from the list
    del ucass                                                           # Delete the ucass object


def process_opts(comm_arr, look_for):
    """
    A function to process a command list, looking for an option
    :param comm_arr: The input command array
    :param look_for: The option flag to look for (e.g. -n, -p, -r)
    :return option: Returns the option after the flag (i.e. -n Foo)
    :return []: If the option is not found
    """
    size = len(comm_arr)
    for i in range(size):               # Cycle through the command array
        if comm_arr[i] == look_for:     # Check the array element against the option flag
            return comm_arr[i+1]        # Return the option variable specified after the flag (i.e. -n Foo)
    return []                           # Return nothing if the option is not found


def list_ports():
    """
    Gets Serial Port Names (**nix only)
    :return port_list: A list of serial ports currently available
    :except serial.SerialException: If a port cannot be opened
    """
    ports = glob.glob('/dev/tty[a-zA-Z]*')              # Use glob to search for anything /dev/tty*
    port_list = []
    for port in ports:
        try:
            s = serial.Serial(port)                     # Check if the port can be opened with pyserial
            s.close()
            port_list.append(port)                      # If the port can be opened, append to list
        except (OSError, serial.SerialException):       # If the port cannot be opened, pass to the next possible port
            pass

    return port_list


def read_config(comm_arr):
    """
    A function to read the config vars from a ucass on a port
    :param comm_arr: The command array entered, only uses -p
    :return []: If no port is specified
    """
    port = process_opts(comm_arr, '-p')                     # Search command array for port
    if not port:
        print "Port not specified"                          # User feedback if no port is specified
        return
    used = port in ucass_list.values()                      # Check if the port is currently in use (with subprocess)
    if used:
        print("Serial port in use with name: %d" % port)    # User feedback if port is used
    else:
        ucass = serial_manager.OPC(port)                    # Start an OPC object from the driver
        ucass.read_info_string()                            # Read the ucass info string
        ucass.read_config_vars()                            # Read the ucass config vars

        # Printing the information and headers to the master command terminal. This is formatted and delimited with '\t'
        # for ease of reading
        print(ucass.info_string)
        print("bb0\tbb1\tbb2\tbb3\tbb4\tbb5\tbb6\tbb7\tbb8\tbb9\tbb10\tbb11\tbb12\tbb13\tbb14\tbb15\tGSC\tID")
        bb_str = "\t".join(str(i) for i in ucass.bbs)
        bb_str = bb_str.replace('[', '')    # Get rid of '[' and ']' from the int -> string conversion
        bb_str = bb_str.replace(']', '')
        sys.stdout.write(bb_str)            # Using sys.stdout so a '\n' is not printed at the end of the line
        sys.stdout.write('\t')
        gsc = str(ucass.gsc)
        gsc = gsc.replace('(', '')          # Removing '(', ')', and ',' from the gsc
        gsc = gsc.replace(')', '')
        gsc = gsc.replace(',', '')
        sys.stdout.write(gsc)
        sys.stdout.write('\t')
        print(str(ucass.id))
