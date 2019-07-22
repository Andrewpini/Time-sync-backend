import socket
import time

DELAY_SEC = 15

UDP_PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

base_data = [0x43, 0x4f, 0x4e, 0x54, 0x52, 0x4f, 0x4c, 0x5f, 0x43, 0x4f, 0x4d, 0x4d, 0x41, 0x4e, 0x44, 0x3a, 0x51, 00]

node_1 = base_data + [0xB0, 0x61, 0x87, 0x8B, 0xDC, 0xD1]
node_2 = base_data + [0xB0, 0xF2, 0xE8, 0x6B, 0xDA, 0x61]
node_3 = base_data + [0xB0, 0x73, 0x4A, 0x9E, 0xAA, 0x57]
node_4 = base_data + [0xB0, 0x55, 0xDF, 0xD8, 0x48, 0xDB]
node_5 = base_data + [0xB0, 0x47, 0x0B, 0xEB, 0xED, 0xA2]
node_6 = base_data + [0xB0, 0x3A, 0x35, 0x65, 0x2E, 0x03]
node_7 = base_data + [0xB0, 0xD0, 0x84, 0x8D, 0xDE, 0x7E]
node_8 = base_data + [0xB0, 0x27, 0x10, 0x22, 0x20, 0x0A]

# *** Nodes on desk ***
# node_1 = base_data + [0xB0, 0x62, 0x40, 0x83, 0xCD, 0xFE]
# node_2 = base_data + [0xB0, 0xEE, 0x2F, 0x91, 0x30, 0x5A]
# node_3 = base_data + [0xB0, 0x32, 0x53, 0x37, 0x27, 0xC5]
# *********************

print("Node 1 DFU")
sock.sendto(bytearray(node_1), ('255.255.255.255', UDP_PORT))
time.sleep(DELAY_SEC)

print("Node 2 DFU")
sock.sendto(bytearray(node_2), ('255.255.255.255', UDP_PORT))
time.sleep(DELAY_SEC)

print("Node 3 DFU")
sock.sendto(bytearray(node_3), ('255.255.255.255', UDP_PORT))
time.sleep(DELAY_SEC)

print("Node 4 DFU")
sock.sendto(bytearray(node_4), ('255.255.255.255', UDP_PORT))
time.sleep(DELAY_SEC)

print("Node 5 DFU")
sock.sendto(bytearray(node_5), ('255.255.255.255', UDP_PORT))
time.sleep(DELAY_SEC)

print("Node 6 DFU")
sock.sendto(bytearray(node_6), ('255.255.255.255', UDP_PORT))
time.sleep(DELAY_SEC)

print("Node 7 DFU")
sock.sendto(bytearray(node_7), ('255.255.255.255', UDP_PORT))
time.sleep(DELAY_SEC)

print("Node 8 DFU")
sock.sendto(bytearray(node_8), ('255.255.255.255', UDP_PORT))
time.sleep(DELAY_SEC)
