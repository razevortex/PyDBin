from type_bases import *

class uint(static_encoded_type):
    __name__ = 'uint_'
    DEFINED = []
    def __init__(self, bits:int|bit):
        if isinstance(bits, bit):
            bits = b2i(bits)
        super().__init__(bits)
        add_define(uint, self.bits)
        self.name = self.__name__ + str(self.bits)

    @property
    def definition(self):
        # the definition property will be writen in the header to initialize specific types
        return [type(self).__name__, self.bits] #static_bit_int.def_type().write_bits(self.bits)

    def _read(self, bits):
        return b2i(bits)

    def _write(self, val):
        if val < 2 ** self.bits:
            return i2b(val, self.bits)
        else:
            print(f'ERROR {val} > {2 ** self.bits}')


class sint(static_encoded_type):
    __name__ = 'sint_'
    DEFINED = []
    def __init__(self, bits:int|bit):
        if isinstance(bits, bit):
            bits = b2i(bits)
        super().__init__(bits)
        add_define(sint, self.bits)
        self.name = self.__name__ + str(self.bits)

    @property
    def definition(self):
        # the definition property will be writen in the header to initialize specific types
        return [type(self).__name__, self.bits]

    def _read(self, bits):
        sign = bits.cut(1)
        return b2i(bits) if b2i(sign) == 0 else -b2i(bits)

    def _write(self, val):
        if abs(val) < 2 ** (self.bits - 1):
            temp = bit([0]) if val >= 0 else bit([1])
            return temp + i2b(val, self.bits - 1)
        else:
            print(f'ERROR {val} > {2 ** (self.bits - 1)}')
