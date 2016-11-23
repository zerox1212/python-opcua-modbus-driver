#!/usr/bin/env python
# -*- coding: utf_8 -*-
"""
 Modbus TestKit: Implementation of Modbus protocol in python

 (C)2009 - Luc Jean - luc.jean@gmail.com
 (C)2009 - Apidev - http://www.apidev.fr

 This is distributed under GNU LGPL license, see license.txt
"""

import serial
import time
import modbus_tk
import modbus_tk.defines as function
from modbus_tk import modbus_rtu
import threading

from serial import serialutil

# Constants
TIMEOUT = 1
REQUEST_DELAY = 0.05

# Create logger object
logger = modbus_tk.utils.create_logger("console")

poll_enable = True


class Slave(object):
    """
    Slave object of IO node with relevant data
    """

    def __init__(self, slave_address, starting_address, read_length, divider, enable):
        self.SlaveAddress = slave_address  # Modbus slave address number
        self.StartingAddress = starting_address  # Modbus starting address
        self.ReadLength = read_length  # Modbus number of registers to read
        self.PollingError = True  # Initialize this slave with an error as no poll attempt has been made yet
        self.Divider = divider  # describes decimal position because slaves only send ints
        self.Enable = enable
        self.Data = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


def poll(slave):
    """
    Poll an individual slave for required data
    """

    try:
        # inter-message delay time
        time.sleep(REQUEST_DELAY)

        try:
            # logger.info(master.execute(slave.SlaveAddress, function.READ_HOLDING_REGISTERS, 0, slave.ReadLength))
            response_data = master.execute(slave.SlaveAddress,
                                           function.READ_HOLDING_REGISTERS,
                                           slave.StartingAddress,
                                           slave.ReadLength)

        except modbus_tk.exceptions.ModbusInvalidResponseError as R_exc:
            logger.error("%s- Code=%d Slave=%d", R_exc, 0, slave.SlaveAddress)
            slave.PollingError = True  # flag this slave as having an unsuccessful read

            # print("Invalid response from slave")

        else:
            # HANDLE MODBUS RESPONSE HERE
            # POPULATE SLAVE OBJECT WITH DATA
            slave.PollingError = False  # reset polling error flag on success
            slave.Data = response_data  # copy the modbus data (tuple) to the slave object
            # print("Slave: ", slave.SlaveAddress, ", Data: ", slave.Data)

    except modbus_tk.modbus.ModbusError as M_exc:
        logger.error("%s- Code=%d", M_exc, M_exc.get_exception_code())
        slave.PollingError = True  # flag this slave as having an unsuccessful read


# polling for all the individual slaves on the network wrapped into a single function for use in a separate thread
def poll_all(slaves):
    """
    Poll all slaves on the network forever - meant to be called in a thread
    """

    while poll_enable:
        # start_time = time.time()
        for slave in slaves:
            if slave.Enable is True:
                poll(slave)

        # end_time = time.time()
        # update_time = (end_time-start_time)*1000
        # logger.info("Network update time: %d", update_time)


# Instantiate slave objects with configuration data in a list
# SlaveObject(Slave Address, Starting Data Address, Read Length, Divider, Enable)
slave_list = [Slave(1, 0, 5, 10, True),
              Slave(2, 0, 10, 10, True),
              Slave(3, 0, 10, 10, True),
              Slave(4, 0, 6, 100, True)]


serial_error = False

# Initialize connection when module is called
try:
    # Connect to the slave (note that the port is 1 less than shown in windows)
    master = modbus_rtu.RtuMaster(serial.Serial(port='COM4',
                                                baudrate=115200,
                                                bytesize=8,
                                                parity='N',
                                                stopbits=2,
                                                xonxoff=0))
    master.set_timeout(TIMEOUT)  # serial timeout in seconds
    master.set_verbose(False)  # logger detail level
    logger.info("RS485 Connected")

except serial.serialutil.SerialException as err:
    print("Serial Error:", err)
    serial_error = True

except modbus_tk.modbus.ModbusError as exc:
    logger.error("%s- Code=%d", exc, exc.get_exception_code())

# Start the thread which communicates to the slaves if there were no serial exceptions raised
if serial_error is False:

    t1 = threading.Thread(target=poll_all, args=[slave_list])
    t1.setDaemon(True)
    t1.start()

# Modbus driver testing
if __name__ == "__main__":
    while True:
        time.sleep(1)



