import random
import driver_ModbusRTU

from ua_object import UaObject
from opcua import ua
from helpers import scale_value


class Device(UaObject):
    """
    Definition of OPC UA object which represents a physical device
    This class mirrors it's UA counterpart and semi-configures itself according to the UA model (from XML)
    """
    def __init__(self, opcua_server, ua_node):
        super().__init__(opcua_server, ua_node)

        self.RawValue = 0
        self.Value = 0.0
        self.Mode = 0
        self.DataSource = ""
        self.DataAddress = ""
        self.SimLowLimit = 0.0
        self.SimHighLimit = 0.0
        self.Location = ""
        self.Description = ""
        self.Units = ""
        self.ScalingEnable = False
        self.RawMin = 0.0
        self.RawMax = 0.0
        self.ScaledMin = 0.0
        self.ScaledMax = 0.0
        self.Divisor = 0.0
        self.User1 = 0.0
        self.User2 = 0.0
        self.User3 = 0.0
        self.User4 = 0.0

    def update(self):
        # Mode=0 is disabled/readonly
        # Mode=1 is normal: get data from configured external data source such as Modbus RTU, etc.
        # Mode=2 is simulation: the tag.Value will be set by the OPC UA server based on the configured limits
        if self.Mode == 0:  # use this mode as "read only" for now; may need to add a separate mode later
            pass
        elif self.Mode == 1:
            if self.DataSource not in (None, '') and self.DataAddress not in (None, ''):
                if self.DataSource == "ModbusRTU":
                    _data_address = self.DataAddress.split(':')
                    _slave = int(_data_address[0]) - 1  # slave is offset in the list by 1 (slave 1 is position 0)
                    _address = int(_data_address[1])

                    # handle raw value
                    _address_value = driver_ModbusRTU.slave_list[_slave].Data[_address] / self.Divisor
                    _dv_raw = ua.DataValue(ua.Variant(_address_value, ua.VariantType.Double))

                    # handle scaled value
                    if self.ScalingEnable:
                        _scaled_value = scale_value(_address_value, self.RawMin, self.RawMax, self.ScaledMin, self.ScaledMax)
                        _dv_val = ua.DataValue(ua.Variant(_scaled_value, ua.VariantType.Double))
                    else:
                        _dv_val = _dv_raw

                elif self.DataSource == "OPCUAClient":
                    pass  # fill in with client to external opc ua server later

                else:
                    _dv_raw = ua.DataValue(ua.Variant(0.0, ua.VariantType.Double))
                    _dv_val = ua.DataValue(ua.Variant(0.0, ua.VariantType.Double))

                # value gets set from configured data source here
                self.nodes['RawValue'].set_data_value(_dv_raw)
                self.nodes['Value'].set_data_value(_dv_val)
            else:
                print("Device {} is on scan has but has invalid configuration".format(self.b_name))
        elif self.Mode == 2:
            self.nodes['Value'].set_value(random.uniform(self.SimLowLimit, self.SimHighLimit))
