import ethernetcomm
import ethernetmsg

handlers = {
    'Ein': str,
    'Swei': ethernetmsg.IAmAliveMsg,
    'Drei': bytes,
}

def handle_iamalive(self, msg):
    pass

msg = ethernetmsg.IAmAliveMsg(b"asdsadasdas234wedsda")

print(msg)

for msgType, handler in handlers.items():
    print(msgType)
    print(handler)

    if isinstance(msg, handler):
        print('Tjohei')
        # handler(self, msg)
