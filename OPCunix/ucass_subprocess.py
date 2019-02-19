import serial_manager
import datetime
import time
import os


def process_opts(command, look_for):
    size = len(command)
    for i in range(size):
        if command[i] == look_for:
            return command[i+1]
    return []


def get_base_name(command):
    name_comm = process_opts(command, '-n')
    d_t = str(datetime.datetime.now())
    d_t = d_t.replace(' ', '_')
    base_name = "UCASS_"
    base_name += name_comm
    base_name += "_"
    base_name += d_t
    return base_name


def make_log(command):
    base_name = get_base_name(command)
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
        name_s = "".join(name_l)
        path_name += '/'
        path_name += name_s
        if os.path.exists(path_name) is False:
            break
    return path_name


module_path = os.path.dirname(os.path.realpath(__file__))
settings_path = module_path + "/ucass_settings.txt"
settings = open(settings_path, "r")
comm = settings.read()
comm_arr = comm.split()
port = process_opts(comm_arr, '-p')
name = process_opts(comm_arr, '-n')
record = process_opts(comm_arr, '-r')
ucass = serial_manager.OPC(port)
res = 0.5

if record == 1:

    log_file_name = make_log(comm_arr)
    ucass.read_config_vars()
    ucass.read_info_string()
    log = open(log_file_name, "a+")
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
    log.flush()
    log.close()

while True:

    ucass.read_histogram_data()
    epoch_time = int(time.time())
    data_array = [epoch_time, ucass.hist, ucass.mtof, ucass.period, ucass.checksum, ucass.reject_glitch,
                  ucass.reject_ltof, ucass.reject_ratio]
    data_array = ",".join(str(i) for i in data_array)
    data_array = data_array.replace('[', '')
    data_array = data_array.replace(']', '')
    print data_array.replace(',', '\t')

    if record == 1:

        log = open(name, "a+")
        log.write(data_array)
        log.write('\n')
        log.flush()
        log.close()

    dt = int(time.time()) - epoch_time

    if dt < res:

        time.sleep(res-dt)

    else:

        print("Exceeded expected resolution, loop time is: %d" % dt)
