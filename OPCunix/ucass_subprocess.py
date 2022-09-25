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
    d_t = datetime.datetime.now()          # Get the date and time
    base_name = f"{d_t:%Y%m%d_%H%M%S}_UCASS_{name_comm}.csv"
    return base_name


def make_log(command):
    """
    A function which makes a log file for the UCASS data
    :param command: the command array from the prompt
    :return path_name: Absolute path name so the file can be opened, closed, and modified in the future
    """
    base_name = get_base_name(command)          # Make the base name, refer to function comments for format
    path = "/home/pi/UCASS/UCASS_A/UCASS_A_DATA/"      # Specify path for log files, should be changed for different UCASS
    directory = os.path.dirname(path)           # Check if the default directory already exists
    if not os.path.exists(directory):
        os.makedirs(directory)                  # Create directory if it doesn't exist

    path_name = f'{path}{base_name}'
    return path_name


def every(delay, task):
    """Function that handles calling a function "task" with some delay without time drift and takes care of exeptions."""
    import time
    import traceback
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
            # in production code you might want to have this instead of course:
            # logger.exception("Problem while executing repetitive task.")
        # skip tasks if we are behind schedule:
        next_time += (time.time() - next_time) // delay * delay + delay


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
if record == "1":                                 # Check if data needs ot be logged
    log_file_name = make_log(comm_arr)          # Get the filename
    ucass.read_config_vars()                    # Read the ucass configuration variables
    ucass.read_info_string()                    # Read the ucass info string
    log = open(log_file_name, "a+")             # Open the log with a+ to append

    # The following code is very similar to that in 'OPCunix.command_handler.read_config'. It is designed to write data
    # and headers to the log file, delimited with ','
    log.write(f'{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S.%f}')
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
    log.write(['UTC DateTime', 'Bin1', 'Bin2', 'Bin3', 'Bin4', 'Bin5', 'Bin6', 'Bin7', 'Bin8',
               'Bin9', 'Bin10', 'Bin11', 'Bin12', 'Bin13', 'Bin14', 'Bin15', 'Bin16',
               'Bin1MToF / us', 'Bin3MToF / us', 'Bin5MToF / us', 'Bin7MToF / us', 'Period',
               'Checksum', 'reject_glitch', 'reject_longtof', 'reject_ratio'])

    # Flush and close the log once recording has finished
    log.flush()
    log.close()

def func():
    # This is the main loop of the subprocess, the number of counts in each particle bin between t and t-1 (known as
    # histogram data) are read through SPI (using the serial_manager purpose made driver), and either simple printed to
    # a screen or recorded and printed to a screen.
    ucass.read_histogram_data()
    date_time = datetime.datetime.utcnow()
    data_array = [date_time, ucass.hist, ucass.mtof, ucass.period, ucass.checksum, ucass.reject_glitch,
                  ucass.reject_ltof, ucass.reject_ratio]
    data_array = ",".join(str(i) for i in data_array)
    data_array = data_array.replace('[', '')
    data_array = data_array.replace(']', '')
    print(data_array.replace(',', '\t'))         # Data for screen is tab delimited for easy reading

    if record == "1":
        log = open(log_file_name, "a+")
        log.write(data_array)
        log.write('\n')
        log.flush()
        log.close()

while True:
	every(res, func)  # Calls function with consistent delay defined by res
