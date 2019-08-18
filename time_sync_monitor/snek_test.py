import ethernetcomm
import ethernetmsg

class snek:

    def __init__(self, greie):

        self.handlers = {
            'handle_iamalive': {'type': ethernetmsg.IAmAliveMsg, 'handler': self.handle_iamalive},
            'handle_string': {'type': str, 'handler': self.handle_string},
            'handle_integer': {'type': int, 'handler': self.handle_integer},
        }
        self.gogogo(greie)

    def handle_iamalive(self, msg):
        print('Pølse')
        print(msg.IP)
        print(msg.element_addr)
        pass

    def handle_string(self):
        print('string')

    def handle_integer(self):
        print('integer')

    def gogogo(self, greie):
        #msg = ethernetmsg.IAmAliveMsg(b"asdsadasdas234wedsda")

        for msgType, handler in self.handlers.items():

            if isinstance(greie, handler['type']):
                handler['handler'](greie)

message = ethernetmsg.Message.get(b'\xce\xfa\xad\xde\xff\xb0b@\x83\xcd\xfe\n\x00\x00\x0c\x03\x00')
print(type(message))
ting = snek(message)
#tang = snek('asd')
#tung = snek(1)