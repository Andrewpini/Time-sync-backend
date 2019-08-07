import socket
import time

UDP_PORT = 10000

blinking_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# blinking_socket.bind(('255.255.255.255', 10000))
blinking_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

data = [0x43, 0x4f, 0x4e, 0x54, 0x52, 0x4f, 0x4c, 0x5f, 0x43,
        0x4f, 0x4d, 0x4d, 0x41, 0x4e, 0x44, 0x3a, 0x28, 0x00]

while(True):
    data[16] = 0x28
    blinking_socket.sendto(bytearray(data), ('255.255.255.255', UDP_PORT))
    print("ON")
    time.sleep(3)

    data[16] = 0x29
    blinking_socket.sendto(bytearray(data), ('255.255.255.255', UDP_PORT))
    print("OFF")
    time.sleep(3)