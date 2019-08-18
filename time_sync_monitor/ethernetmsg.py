from struct import *
from ethernetmsgtypes import *
from uuid import getnode as get_mac

IDENTIFIER = 0xDEADFACE
OPCODES = {
    'IAmAliveMsg': -1,
    'StartSyncLineMsg': -2,
    'StopSyncLineMsg': -3,
    'StartTimeSyncMsg': -4,
    'StopTimeSyncMsg': -5,
    'StartSyncLineAckMsg': -6,
    'StopSyncLineAckMsg': -7,
    'StartTimeSyncAckMsg': -8,
    'StopTimeSyncAckMsg': -9,
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

    def __init__(self, raw_data=None):
        #Creating a outgoing message
        if raw_data is None:
            self.identifier = IDENTIFIER
            self.mac = get_mac_addr()
            self.opcode = None
        #Parsing an incoming message
        else:
            self.identifier = None
            self.mac = None
            self.opcode = None
            self.payload = self.parse_header(raw_data)

    @staticmethod
    def get(raw_data): # factory pattern
        msg = Message(raw_data)
        if msg.opcode == OPCODES['IAmAliveMsg']:
            return IAmAliveMsg(raw_data)
        if msg.opcode == OPCODES['StartSyncLineMsg']:
            return StartSyncLineMsg(raw_data)
        if msg.opcode == OPCODES['StopSyncLineMsg']:
            return StopSyncLineMsg(raw_data)
        if msg.opcode == OPCODES['StartTimeSyncMsg']:
            return StartTimeSyncMsg(raw_data)
        if msg.opcode == OPCODES['StopTimeSyncMsg']:
            return StopTimeSyncMsg(raw_data)
        if msg.opcode == OPCODES['StartSyncLineAckMsg']:
            return StartSyncLineAckMsg(raw_data)
        if msg.opcode == OPCODES['StopSyncLineAckMsg']:
            return StopSyncLineAckMsg(raw_data)
        if msg.opcode == OPCODES['StartTimeSyncAckMsg']:
            return StartTimeSyncAckMsg(raw_data)
        if msg.opcode == OPCODES['StopTimeSyncAckMsg']:
            return StopTimeSyncAckMsg(raw_data)

    def parse_header(self, raw_data):
        (self.identifier, self.opcode, self.mac) = unpack_from(Message.HEADER_FORMAT, raw_data, 0)
        self.mac = MACAddr(self.mac)
        return raw_data[11:]

    def pack_header(self):
        return pack(Message.HEADER_FORMAT, self.identifier, self.opcode, bytes(self.mac))


class SimpleSignalMsg(Message):
    MESSAGE_FORMAT = '=6s'
    def __init__(self, opcode, raw_data=None):
        super().__init__(raw_data)
        #Creating a outgoing message
        if raw_data is None:
            self.opcode = opcode
        #Parsing an incoming message
        else:
            #self.parse_msg(self.payload)
            pass

    def get_packed_msg(self, reciever_addr):
        header = self.pack_header()
        msg = pack(self.MESSAGE_FORMAT, bytes(reciever_addr))
        return header + msg

class IAmAliveMsg(Message):
    MESSAGE_FORMAT = '=4sh'

    def __init__(self, raw_data=None):
        super().__init__(raw_data)
        #Creating a outgoing message
        if raw_data is None:
            self.opcode = OPCODES['IAmAliveMsg']
            #TODO: Comment out at some point
            self.IP = [4,5,2,7]
            self.element_addr = 0x1111
        #Parsing an incoming message
        else:
            self.IP = None
            self.element_addr = None
            self.parse_msg(self.payload)
            self.ID_string = "%s | %s | %s" % (self.IP, self.mac, self.element_addr)

    def parse_msg(self, payload):
        if payload is not None:
            (self.IP, self.element_addr) = unpack_from(IAmAliveMsg.MESSAGE_FORMAT, payload, 0)
            self.IP = IPAddr(self.IP)
            self.element_addr = ElementAddr(self.element_addr)

    def get_packed_msg(self):
        header = self.pack_header()
        msg = pack(self.MESSAGE_FORMAT, bytes(self.IP), self.element_addr)
        return header + msg


class StartSyncLineMsg(SimpleSignalMsg):
    def __init__(self, raw_data=None):
        super().__init__(OPCODES['StartSyncLineMsg'], raw_data)


class StopSyncLineMsg(SimpleSignalMsg):
    def __init__(self, raw_data=None):
        super().__init__(OPCODES['StopSyncLineMsg'], raw_data)


class StartTimeSyncMsg(SimpleSignalMsg):
    def __init__(self, raw_data=None):
        super().__init__(OPCODES['StartTimeSyncMsg'], raw_data)


class StopTimeSyncMsg(SimpleSignalMsg):
    def __init__(self, raw_data=None):
        super().__init__(OPCODES['StopTimeSyncMsg'], raw_data)
      
       
class StartSyncLineAckMsg(SimpleSignalMsg):
    def __init__(self, raw_data=None):
        super().__init__(OPCODES['StartSyncLineAckMsg'], raw_data)


class StopSyncLineAckMsg(SimpleSignalMsg):
    def __init__(self, raw_data=None):
        super().__init__(OPCODES['StartSyncLineAckMsg'], raw_data)


class StartTimeSyncAckMsg(SimpleSignalMsg):
    def __init__(self, raw_data=None):
        super().__init__(OPCODES['StartTimeSyncAckMsg'], raw_data)


class StopTimeSyncAckMsg(SimpleSignalMsg):
    def __init__(self, raw_data=None):
        super().__init__(OPCODES['StopTimeSyncAckMsg'], raw_data)

