from struct import *
from ethernetmsgtypes import *



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

    @staticmethod
    def get_opcode(raw_data): # factory pattern
        return unpack_from('b', raw_data, 4)

    def parse_header(self, raw_data):
        (self.identifier, self.opcode, self.mac) = unpack_from(Message.HEADER_FORMAT, raw_data, 0)
        self.mac = MACAddr(self.mac)
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
        self.IP = IPAddr(self.IP)
        self.element_addr = ElementAddr(self.element_addr)

# msg = Message.get(b'\xce\xfa\xad\xde\xff\xb0\x95U;\x94\xa4\n\x00\x00\x0b\x04\x00')
#
# print(msg.IP)
# print(bytes(msg.IP))
# print(msg.mac)
# print(bytes(msg.mac))


# b'\xce\xfa\xad\xde\xff\xb0\x95U;\x94\xa4\n\x00\x00\x0b\xaf\x10'