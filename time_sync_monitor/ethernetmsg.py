from struct import *
from array import *

def make_MAC_pretty(raw_mac_addr):
    pretty_mac = ''
    pretty_mac += raw_mac_addr[0:2]
    for i in range (2, 12, 2):
        pretty_mac += '-' + raw_mac_addr[i:i+2]
    pretty_mac = pretty_mac.upper()
    print(pretty_mac)

class Message:

    HEADER_FORMAT = '=Ib6s'

    def __init__(self, raw_data):
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
        y = bytes
        (self.identifier, self.opcode, y) = unpack_from(Message.HEADER_FORMAT, raw_data, 0)
        print(self.identifier)
        print(self.opcode)
        print(self.mac)
        print(y)
        return raw_data[11:]

    def pack_header(self):
        return pack(Message.HEADER_FORMAT, self.ip, self.mac, self.opcode)


class IAmAliveMsg(Message):
    MESSAGE_FORMAT = '=4sh'

    def __init__(self, raw_data):
        super().__init__(raw_data)
        self.IP = None
        self.element_addr = None
        self.parse_msg(self.payload)

    def parse_msg(self, payload):
        (self.IP, self.element_addr) = unpack_from(IAmAliveMsg.MESSAGE_FORMAT, payload, 0)
        print(self.IP)
        print(hex(self.element_addr))


msg = IAmAliveMsg.get(b'\xce\xfa\xad\xde\xff\xb0b@\x83\xcd\xfe\n\x00\x00\x0c\x03\x00')
make_MAC_pretty('b0a17cffe356')


