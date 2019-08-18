from struct import *
from ethernetmsgtypes import *
from uuid import getnode as get_mac

OPCODES = {
    'IAmAliveMsg': -1,
    'StartSyncLineMsg': -2
}

def get_mac_addr():
    mac = get_mac()
    mac_list = []
    for i in range(2, 14, 2):
        element = str(hex(mac))[i:i + 2]
        int_element = int(element, 16)
        mac_list.append(int_element)
    return mac_list

class Message:

    HEADER_FORMAT = '=Ib6s'
    IDENTIFIER = 0xDEADFACE

    def __init__(self, raw_data=None):
        self.identifier = None
        self.mac = None
        self.opcode = None
        self.payload = self.parse_header(raw_data)

    @staticmethod
    def get(raw_data): # factory pattern
        msg = Message(raw_data)
        if msg.opcode == -1:
            return IAmAliveMsg(raw_data)

    def parse_header(self, raw_data):
        if raw_data is not None:
            (self.identifier, self.opcode, self.mac) = unpack_from(Message.HEADER_FORMAT, raw_data, 0)
            self.mac = MACAddr(self.mac)
            return raw_data[11:]
        else:
            return None

    def pack_header(self):
        return pack(Message.HEADER_FORMAT, self.identifier, self.opcode, self.mac,)


class IAmAliveMsg(Message):
    MESSAGE_FORMAT = '=4sh'

    def __init__(self, raw_data=None):
        super().__init__(raw_data)
        self.IP = None
        self.element_addr = None
        self.parse_msg(self.payload)
        self.ID_string = "%s | %s | %s" % (self.IP, self.mac, self.element_addr)

    def parse_msg(self, payload):
        if payload is not None:
            (self.IP, self.element_addr) = unpack_from(IAmAliveMsg.MESSAGE_FORMAT, payload, 0)
            self.IP = IPAddr(self.IP)
            self.element_addr = ElementAddr(self.element_addr)



class StartSyncLineMsg(Message):
    MESSAGE_FORMAT = '=6s'

    def __init__(self, raw_data):
        super().__init__(raw_data)


ting = IAmAliveMsg()





# msg = Message.get(b'\xce\xfa\xad\xde\xff\xb0\x95U;\x94\xa4\n\x00\x00\x0b\x04\x00')
#
# print(msg.IP)
# print(bytes(msg.IP))
# print(msg.mac)
# print(bytes(msg.mac))


# b'\xce\xfa\xad\xde\xff\xb0\x95U;\x94\xa4\n\x00\x00\x0b\xaf\x10'