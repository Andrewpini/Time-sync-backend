import ethernetcomm
import ethernetmsg
import struct
import socket
import uuid

# printing the value of unique MAC
# address using uuid and getnode() function
print(hex(uuid.getnode()))

asd = struct.pack('=Ib6s4sh', 0xDEADFACE, -1, bytes([0xB0, 0x95, 0x55, 0x3B, 0x94, 0xA4]), bytes([10, 0, 0, 11]), 0x4)
print(asd)

ip = socket.gethostbyname_ex(socket.gethostname())
#mac = socket.get
print(ip)
#b'\xce\xfa\xad\xde\xff\xb0\x95U;\x94\xa4\n\x00\x00\x0b\x04\x00'
#'=Ib6s4sh'
