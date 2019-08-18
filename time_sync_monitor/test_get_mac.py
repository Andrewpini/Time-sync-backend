from uuid import getnode as get_mac
mac = get_mac()
list = []
for i in range(2, 14, 2):
    element = str(hex(mac))[i:i+2]
    int_element = int(element, 16)
    list.append(int_element)




'''
    for i in range(2, 14, 2):

    element = str(hex(mac))[i:i+2]
    int_element = int(element, 16)
    list.append(int_element)

   '''