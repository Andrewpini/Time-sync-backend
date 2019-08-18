
class IPAddr:
    def __init__(self, bytearray):
        self.value = bytearray

    def __bytes__(self):
        return self.value

    def __str__(self):
        return '%d.%d.%d.%d' % tuple(self.value)

class MACAddr:
    def __init__(self, bytearray):
        self.value = bytearray

    def __bytes__(self):
        return self.value

    def __str__(self):
        return '%X-%X-%X-%X-%X-%X' % tuple(self.value)

class ElementAddr:
    def __init__(self, bytearray):
        self.value = bytearray

    def __bytes__(self):
        return self.value

    def __str__(self):
        return '0x%04X' % self.value

