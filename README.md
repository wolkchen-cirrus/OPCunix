# OPCunix
This software is designed to comminicate with the universal cloud and aerosol sounding system (UCASS) optical particle counter (OPC) designed at the University of Hertfordshire.
***
# Hardware #
This software has the ability to handle multiple UCASS units simultaneously, all units must be connected before the software is started. Use a USB-ISS interface to connect a unit to the computer, the interface must be connected to the SPI pins of the UCASS (this usually has a breakout connector attached for this purpose).
***
# Installation #
Install this software using pip:

`pip install OPCunix`

Then create a shortcut to where the 'main.py' file is located, or create a shell script with the following:

`#!/bin/bash`  \n
`python ${PATH_TO_MODULE}/main.py`

***
