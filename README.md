# OPCunix #
This software is designed to comminicate with the universal cloud and aerosol sounding system (UCASS) optical particle counter (OPC) designed at the University of Hertfordshire.
***
## Hardware ##
This software has the ability to handle multiple UCASS units simultaneously, all units must be connected before the software is started. Use a USB-ISS interface to connect a unit to the computer, the interface must be connected to the SPI pins of the UCASS (this usually has a breakout connector attached for this purpose).
***
## Installation ##
Install this software using pip:

`pip install UH-OPCunix-JGirdwood`

Use your prefered downloader (wget used here) to download the main.py file from github into a directory of your choice:

`wget https://github.com/JGirdwood/OPCunix/raw/master/main.py`

Then run the main file directly, create a shortcut to where the 'main.py' file is located, or create a shell script with the following:

`#!/bin/bash`  
`python ${PATH_TO_MODULE}/main.py`

### Dependancies ###
This module requires the following modules to be installed with pip, in addition to the default python modules:

`pip install pyserial pyusbiss`

***
## Commands ##
The parent process in this software is a terminal program from which several different commands can be launched. Options can be specified with the commands using '-' e.g. '-n', '-p', etc. A full list of commands is displayed here:

* `[OPC-unix] >> list ports`  - Lists all the serial ports available
* `[OPC-unix] >> list ucass`  - Lists all the initialised UCASS units
* `[OPC-unix] >> clear`       - Clears the screen
* `[OPC-unix] >> exit`        - Exits the program
* `[OPC-unix] >> ucass`       - The master for the commands associated with UCASS interfacing:
    1. init                   - Initialises a UCASS unit and starts recording histogram data in a subprocess (new window)
        *   Options:
            1.  '-n'          - User specified name for the unit, used to keep track
            2.  '-p'          - Port to start the comminications on (i.e. /dev/tty*)
            3.  '-r'          - Record to file or not (boolean 1 or 0), this will also print config vars to log
    2. del                    - Deletes a UCASS unit and shuts down the subprocess
        *   Options:
            1.  '-n'          - Specify the name of the unit (set during init) you want to delete
    3.  conf                  - Read config vars and print in parent process
        *   Options:
            1.  '-p'          - Specify the port of the unit you want to read (note this cannot be in use with init)

### Examples ###
*Example given, to initialise a UCASS unit to print histogram data to a screen:*

`[OPC-unix] >> list ports`

This will return a list of ports e.g.:

`['/dev/ttyACM0']`

Next, list the config vars so the bin bounderies are known or checked:

`[OPC-unix] >> ucass conf -p /dev/ttyACM0`

This will return the tab delimited configuration variables (and headers) printed to the terminal window. Next, start recording histogram data:

`[OPC-unix] >> ucass init -n unit-E -p /dev/ttyACM0 -r 1`

This will initialise a UCASS with name 'unit-E' on port '/dev/ttyACM0' and start recording to a file in a directory specified by the 'default_path.txt' file in the module. By default this is ${HOME}/UCASS_LOG/ (the directory will be created automatically if it does not exist). This command will also start a new terminal window, which will be printing out data.













