import sys
sys.path.insert(0, "..")
import time
import driver_ModbusRTU  # importing will start the modbus communications thread
import threading

from opcua import ua, Server, Node
from helpers import find_o_types
from device import Device


class OPCUAServer(object):

    def __init__(self):
        self.server = None
        self.uri = ""
        self.idx = 0
        self.scan_thread = None
        self.scan_enable = False
        self.devices = []

        # setup our server
        self.server = Server()
        self.server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

        # setup our own namespace, not really necessary but should as spec
        uri = "http://examples.freeopcua.github.io"
        idx = self.server.register_namespace(uri)

        # import address space which has a device object
        self.server.import_xml("device.xml")

        # get Objects node
        objects = self.server.get_objects_node()

        # get the device object type so we can find all the devices in the address space
        hw_type = self.server.nodes.base_object_type.get_child("2:Device")
        device_nodes = find_o_types(objects, hw_type)

        # instantiate a device python object and make it an attribute of the server class
        # FIXME do your own organization, most likely an object oriented model
        for device_node in device_nodes:
            device = Device(self.server, device_node)
            setattr(self, device.b_name, device)
            # keep track of the device because so that we can update it cyclically using the driver
            self.devices.append(device)

    def _scan(self):
        while self.scan_enable:
            # update all device data from devices' configured driver, such as modbus)
            for device in self.devices:
                device.update()

            time.sleep(1)

    def scan_on(self):
        # Start the thread which handles the cyclic updates of devices
        self.scan_thread = threading.Thread(target=self._scan)
        # self.scan_thread.setDaemon(True)
        self.scan_enable = True
        self.scan_thread.start()

    def scan_off(self):
        # Stop the thread which handles cyclic updates
        self.scan_enable = False
        self.scan_thread.join()


if __name__ == "__main__":

    # Create a server
    my_server = OPCUAServer()

    # start scanning for cyclic updates
    my_server.scan_on()
