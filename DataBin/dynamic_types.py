from type_base import *

class bit_int(length_encoded_type):
  __name__ = 'int'
    def __init__(self, *args):
        super().__init__(4)

    def __eq__(self, other):
        if type(other) == int:
            return True
        else:
            return False

    def _encoding(self, bits:bit):
        return [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768][b2i(bits)] + 1 #2 ** b2i(bits) + 1 # returns the length in bits of the integer

    def _read(self, bits:bit):
        sign = bits.cut(1)
        return b2i(bits) if b2i(sign) == 0 else -b2i(bits)

    def _decoding(self, val:int):
        for i, v in enumerate([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]):
            if 2 ** v > abs(val):
                return i
        print(f'ERROR {val} is to large')

    def _write(self, value:int, length:int):
        temp = bit([0]) if value >= 0 else bit([1])
        return i2b(length, self.bits) + temp + i2b(abs(value), 2**length)


# char is not a type on its own its more a char set used by str types
class bit_schar(static_encoded_type):
    def __init__(self):
        super().__init__(8)
        self.chars = [chr(i) for i in range(256)]
        self.name = 'native_char'

    def _read(self, bits:bit):
        return chr(b2i(bits.cut(self.bits)))

    def _write(self, val):
        return i2b(ord(val), self.bits)

class bit_str(endbit_encoded_type):
    __name__ = 'str'
    def __init__(self, *args):
        self.chars = bit_schar()
        super().__init__(self.chars.bits, i2b(0, self.chars.bits))

    def __eq__(self, other):
        if type(other) == str:
            return True
        else:
            return False

    def read_bits(self, bits:bit):
        bits = super().read_bits(bits)
        string = ''
        while len(bits) >= self.bits:
            string += self.chars.read_bits(bits)
        return string

    def write_bits(self, val):
        temp = bit()
        for char in str(val):
            temp += self.chars.write_bits(char)
        return super().write_bits(temp)


class bit_fchar(static_encoded_type):
    def __init__(self):
        super().__init__(4)
        self.chars = [char for char in '1234567890.-: '] # The ' ' and ':' are included since there where these unused values anyway and like this it can be used for datetimes later on
        self.name = 'fchar'

    def _read(self, bits):
        return self.chars[b2i(bits.cut(self.bits))]

    def _write(self, val):
        return i2b(self.chars.index(val), self.bits)

class bit_float(endbit_encoded_type):
    __name__ = 'float'
    def __init__(self, *args):
        self.chars = bit_fchar()
        super().__init__(self.chars.bits, i2b(15, 4))

    def __eq__(self, other):
        if type(other) == float:
            return True
        else:
            return False

    def read_bits(self, bits):
        bits = super().read_bits(bits)
        return float(''.join([self.chars.read_bits(bits) for _ in range(len(bits) // self.bits)]))

    def write_bits(self, val):
        temp = bit()
        for char in str(val):
            temp += self.chars.write_bits(char)
        return super().write_bits(temp)


class bit_list(endbit_encoded_type):
    __name__ = 'list'
    types = DynamicTypes

    def __init__(self, *args):
        self.types = bit_list.types()
        super().__init__(1, i2b(0, 1))

    def __eq__(self, other):
        if type(other) == list:
            return True
        else:
            return False

    def read_bits(self, bits:bit):
        temp = []
        while bits.cut(self.bits) != self.stop_sequence:
            temp.append(self.types.read_bits(bits))
        return temp

    def write_bits(self, value):
        temp = bit()
        for item in value:
            print(item)
            temp += i2b(1, self.bits) + self.types.write_bits(item)
        return temp + self.stop_sequence
        return temp + self.stop_sequence


class bit_tuple(endbit_encoded_type):
    __name__ = 'tuple'
    types = DynamicTypes
    def __init__(self):
        self.types = bit_tuple.types()
        super().__init__(1, i2b(0, 1))

    def __eq__(self, other):
        if type(other) == tuple:
            return True
        else:
            return False

    def read_bits(self, bits:bit):
        temp = []
        while bits.cut(self.bits) != self.stop_sequence:
            temp.append(self.types.read_bits(bits))
        return tuple(temp)

    def write_bits(self, value):
        temp = bit()
        for item in value:
            temp += i2b(1, self.bits) + self.types.write_bits(item)
        return temp + self.stop_sequence


class bit_dict(endbit_encoded_type):
    __name__ = 'dict'
    types = DynamicTypes
    def __init__(self):
        self.types = bit_dict.types()
        super().__init__(1, i2b(0, 1))

    def __eq__(self, other):
        if type(other) == dict:
            return True
        else:
            return False

    def read_bits(self, bits:bit):
        temp = {}
        while bits.cut(self.bits) != self.stop_sequence:
            key = self.types.read_bits(bits)
            temp[key] = self.types.read_bits(bits)
        return temp

    def write_bits(self, value):
        temp = bit()
        for key, val in value.items():
            temp += i2b(1, self.bits) + self.types.write_bits(key) + self.types.write_bits(val)
        return temp + self.stop_sequence



class bit_bool(static_encoded_type):
    __name__ = 'bool'
    def __init__(self, *args):
        super().__init__(1)

    def __eq__(self, other):
        if type(other) == bool:
            return True
        else:
            return False

    def _read(self, bits:bit):
        return (False, True)[b2i(bits)]

    def write_bits(self, val):
        return i2b(int(val), self.bits)

class bit_none(static_encoded_type):
    __name__ = 'NoneType'
    def __init__(self, *args):
        super().__init__(0)

    def __eq__(self, other):
        if other is None:
            return True
        else:
            return False

    def read_bits(self, bits:bit):
        return None

    def write_bits(self, val):
        return bit()
