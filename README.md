# OPCunix #
This software is designed to comminicate with the universal cloud and aerosol sounding system (UCASS) optical particle counter (OPC) designed at the University of Hertfordshire.
***
## Hardware ##
This software has the ability to handle multiple UCASS units simultaneously, all units must be connected before the software is started. Use a USB-ISS interface to connect a unit to the computer, the interface must be connected to the SPI pins of the UCASS (this usually has a breakout connector attached for this purpose).
***
## Installation ##
Install this software using pip:

`pip install OPCunix`

Then create a shortcut to where the 'main.py' file is located, or create a shell script with the following:

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
    1. init                   - Initialises a ucass unit and starts recording histogram data in 
