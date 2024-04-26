from BitObj import *

class length_encoded_type(object):
    DEFINED = None
    __name__ = ''
    __slots__ = 'name', 'bits', 'encoding', 'decoding'
    def __init__(self, bits):
        self.bits = bits
        self.encoding = self._encoding
        self.decoding = self._decoding
        self.name = self.__name__

    @property
    def definition(self):
        return bit()

    def _encoding(self, *args):
        # defined in Child
        return None

    def _decoding(self, *args):
        # defined in Child
        return None

    def _read(self, *args):
        return None

    def _write(self, *args):
        return None

    def read_bits(self, bits:bit):
        length = self.encoding(bits.cut(self.bits))
        return self._read(bits.cut(length))

    def write_bits(self, value):
        length = self.decoding(value)
        if not length is None:
            return self._write(value, length)

    def conversion(self, in_):
        if isinstance(in_, bit):
            return self.read_bits(in_)
        return self.write_bits(in_)

class endbit_encoded_type(object):
    DEFINED = None
    __name__ = ''
    __slots__ = 'name', 'bits', 'stop_sequence'
    def __init__(self, bits, stop_sequence):
        self.bits, self.stop_sequence = bits, stop_sequence
        self.name = self.__name__

    @property
    def definition(self):
        return bit()

    def read_bits(self, bits:bit):
        i = 0
        temp, _t = bit(), bits.cut(self.bits)
        while _t != self.stop_sequence and len(_t) == self.bits:
            temp += _t
            _t = bits.cut(self.bits)
        return temp

    def write_bits(self, value):
        return value + self.stop_sequence

    def conversion(self, in_):
        if isinstance(in_, bit):
            return self.read_bits(in_)
        return self.write_bits(in_)


# some predefined set of types with static lengths
class static_encoded_type(object):
    __name__ = ''
    DEFINED = None
    def_type = None
    __slots__ = 'name', 'bits'
    def __init__(self, bits:int|bit):
        if isinstance(bits, bit):
            bits = b2i(bits)
        self.bits = bits
        self.name = self.__name__

    @property
    def definition(self):
        return bit()

    def _read(self, bits:bit):
        return None

    def _write(self, value):
        return None

    def read_bits(self, bits:bit):
        return self._read(bits.cut(self.bits))

    def write_bits(self, value):
        return self._write(value)

    def conversion(self, in_):
        if isinstance(in_, bit):
            return self.read_bits(in_)
        return self.write_bits(in_)

def add_define(_type, definition):
    if definition not in _type.DEFINED:
        _type.DEFINED.append(definition)
