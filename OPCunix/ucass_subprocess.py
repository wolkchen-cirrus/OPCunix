import serial_manager
import command_handler
import datetime
import time


settings = open("ucass_settings.txt", "r")
comm_arr = settings.read()
port = command_handler.process_opts(comm_arr, '-p')
name = command_handler.process_opts(comm_arr, '-n')
record = command_handler.process_opts(comm_arr, '-r')
ucass = serial_manager.OPC(port)
res = 0.5

if record == 1:

    log_file_name = command_handler.make_log(comm_arr)
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

