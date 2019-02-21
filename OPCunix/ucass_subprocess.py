import serial_manager
import datetime
import time
import os


def process_opts(command, look_for):
    """
    Refer to 'OPCunix.command_handler.process_opts' for details
    """
    size = len(command)
    for i in range(size):
        if command[i] == look_for:
            return command[i+1]
    return []


def get_base_name(command):
    """
    A function to get the base name of the log file in format UCASS_"name"_YYY-MM-DD_HH:MM:SS.SSSS
    :param command: The command array from the ucass_settings.txt file
    :return base_name: the name to use as a base for the log file (added is "_XX.csv" where XX is a version number")
    """
    name_comm = process_opts(command, '-n')     # Get the name from the command
    d_t = str(datetime.datetime.now())          # Get the date and time in a string
    d_t = d_t.replace(' ', '_')                 # Format the date-time string

    # Making the base_name string in the stated format. This will be UCASS_"name"_YYY-MM-DD_HH:MM:SS.SSSS, and _XX.csv
    # will be added after this (where XX is a version number) to ensure the string does not get overwritten when the
    # date and time cannot be obtained.
    base_name = "UCASS_"
    base_name += name_comm
    base_name += "_"
    base_name += d_t
    return base_name


def make_log(command):
    """
    A function which makes a log file for the UCASS data
    :param command: the command array from the prompt
    :return path_name: Absolute path name so the file can be opened, closed, and modified in the future
    """
    base_name = get_base_name(command)          # Make the base name, refer to function comments for format
    path_file = open("default_path.txt", "r")   # Get the default file path from the settings file
    path = path_file.read()
    base_name += "_00.csv"                      # Add the extension to the base name
    directory = os.path.dirname(path)           # Check if the default directory already exists
    if not os.path.exists(directory):
        os.makedirs(directory)                  # Create directory if it doesn't exist

    # This loop is designed to step the "_00.csv" by one if the filename already exists, to prevent files being
    # overwritten when time and data data cannot be obtained.
    path_name = path
    for i in range(100):
        path_name = path
        name_l = list(base_name)
        name_l[-1 - 5] = str(int(i / 10))
        name_l[-1 - 4] = str(int(i % 10))
        name_s = "".join(name_l)
        path_name += '/'
        path_name += name_s
        if os.path.exists(path_name) is False:
            break
    return path_name


module_path = os.path.dirname(os.path.realpath(__file__))   # Get the absolute path of this module directory

# The commands and variables for this subprocess is sent from the master process (command_handler) using a file called
# 'ucass_settings.txt'. The command to run this process is written to the settings file before the subprocess is
# started. The following code is designed to read this file and process the commands into variables
settings_path = module_path + "/ucass_settings.txt"         # Path to the settings file
settings = open(settings_path, "r")
comm = settings.read()
comm_arr = comm.split()                                     # Split up the command delimited by ' '
port = process_opts(comm_arr, '-p')
name = process_opts(comm_arr, '-n')
record = process_opts(comm_arr, '-r')
ucass = serial_manager.OPC(port)                            # Start an instance of the OPC class from the driver

res = 0.5                                                   # Temporal resolution in seconds

if record == 1:                                 # Check if data needs ot be logged

    log_file_name = make_log(comm_arr)          # Get the filename
    ucass.read_config_vars()                    # Read the ucass configuration variables
    ucass.read_info_string()                    # Read the ucass info string
    log = open(log_file_name, "a+")             # Open the log with a+ to append

    # The following code is very similar to that in 'OPCunix.command_handler.read_config'. It is designed to write data
    # and headers to the log file, delimited with ','
    date_time = str(datetime.datetime.now())
    date_time = date_time.replace(' ', ',')
    log.write(date_time)
    log.write('\n')
    log.write(name)
    log.write(',')
    log.write(ucass.info_string)
    log.write('\n')
    log.write("bb0,bb1,bb2,bb3,bb4,bb5,bb6,bb7,bb8,bb9,bb10,bb11,bb12,bb13,bb14,bb15,GSC,ID\n")
    bb_str = ",".join(str(i) for i in ucass.bbs)
    bb_str = bb_str.replace('[', '')
    bb_str = bb_str.replace(']', '')
    log.write(bb_str)
    log.write(',')
    log.write(str(ucass.gsc))
    log.write(',')
    log.write(str(ucass.id))
    log.write('\n')
    log.write("time,b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12,b13,b14,b15,b1ToF,b3ToF"
              ",b7ToF,period,CSum,glitch,longToF,RejRat\n")

    # Flush and close the log once recording has finished
    log.flush()
    log.close()

while True:

    # This is the main loop of the subprocess, the number of counts in each particle bin between t and t-1 (known as
    # histogram data) are read through SPI (using the serial_manager purpose made driver), and either simple printed to
    # a screen or recorded and printed to a screen.
    ucass.read_histogram_data()
    epoch_time = int(time.time())
    data_array = [epoch_time, ucass.hist, ucass.mtof, ucass.period, ucass.checksum, ucass.reject_glitch,
                  ucass.reject_ltof, ucass.reject_ratio]
    data_array = ",".join(str(i) for i in data_array)
    data_array = data_array.replace('[', '')
    data_array = data_array.replace(']', '')
    print data_array.replace(',', '\t')         # Data for screen is tab delimited for easy reading

    if record == 1:

        log = open(name, "a+")
        log.write(data_array)
        log.write('\n')
        log.flush()
        log.close()

    # The following code is to define the temporal resolution of measurements
    dt = int(time.time()) - epoch_time          # Check how long the loop took to process

    if dt < res:
        time.sleep(res-dt)                      # Make sure the loop time is = 'res'
    else:                                       # User feedback if the resolution is too high
        print("Exceeded expected resolution, loop time is: %d" % dt)
