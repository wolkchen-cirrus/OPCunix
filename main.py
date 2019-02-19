import OPCunix


OPCunix.command_handler.make_title()
while True:
    command = raw_input("[OPC-unix] >> ")
    c = OPCunix.command_handler.process(command)
    if c == 0:
        break
