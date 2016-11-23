# python-opcua-modbus-driver
Python OPC UA Modbus Driver
  
Elementary implementaion which bridges Modbus RTU data to OPC UA server.  
  
The basic principle is this:  
1. Start `server_minimal.py`  
2. This will import the `driver_ModbusRTU.py` which will kick off a thread which scans a modbus network  
3. The server will import an XML file which has an Object Type for a hardware device, the example has one device (MyDevice)  
4. The server will instantiate a python `Device` object which has an `update` method for getting data from Modbus  
5. MyDevice links to the modbus driver via parameters from OPC UA, so it can be configued from an HMI or UA client  

This example is not tested and has never been run. It is a generic starting point created from a working implementation.
