import OPCunix


OPCunix.command_handler.make_title()
while True:
    command = input("[OPC-unix] >> ")
    c = OPCunix.command_handler.process(command)
    if c == 0:
        break
