from BitObj import *

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#    Base Type Parent Classes                                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#    Dynamic Types                                                                                                        #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

#                                          Int
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

#                                          Str

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

#                                          Float

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

#                                          List

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

#                                          Tuple

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

#                                          Dict

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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#    Literal Types                                                                                                        #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

#                                          Bool

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

#                                          NoneType

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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#    Static Types                                                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

#                                          Int

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

#                                          Float

class sfloat(static_encoded_type):
    __name__ = 'sfloat_'
    DEFINED = []
    def __init__(self, bits):
        if isinstance(bits, bit):
            bits = b2i(bits)
        super().__init__(4 * bits)
        add_define(ufloat, bits)
        self.chars = bit_fchar()

    def _read(self, bits):
        return float(''.join([self.chars.read_bits(bits) for _ in range(len(bits) // 4)]))

    def _write(self, val):
        temp = bit()
        val = str(val).lstrip('0') + '0' * (self.bits // 4)
        for i in range(self.bits // 4):
            temp += self.chars.write_bits(val[i])
        return temp

#                                          Str

class sstr_list(list):
    def __init__(self):
        super().__init__()

    def append(self, other):
        if type(other) != tuple:
            return
        try:
            a = self.pop(0)
        except:
            a = ()
        temp = []
        [temp.append(string) for string in a + other if string not in temp]
        super().append(tuple(temp))

class sstr(static_encoded_type):
    __name__ = 'sstr'
    DEFINED = sstr_list()
    def __init__(self, bits:tuple|bit):
        self.name = 'sstr'
        if isinstance(bits, bit):
            self.words = DynamicTypes().read_bits(bits)
        sstr.DEFINED.append(bits)
        self.words = sstr.DEFINED[0]

    @property
    def definition(self):
        return (type(self).__name__, self.words)

    @property
    def bits(self):
        i = 0
        while 2 ** i <= len(self.words):
            i += 1
        return i

    def _write(self, value):
        print(self.words)
        if type(value) == str:
            return i2b(self.words.index(value), self.bits)

    def _read(self, bits):
        return self.words[b2i(bits)]

#                                          Tuple

class tuple_T(static_encoded_type):
    DEFINED = []
    __name__ = 'tuple_T_'
    def __init__(self, *_items):
        self.items = [item for item in _items]
        super().__init__(sum([t.bits for t in self.items]))
        self.name = f'{tuple_T.__name__}{len(self.items)}_{self.bits}'
        add_define(tuple_T, self.definition[1])

    @property
    def definition(self):
        return [type(self).__name__, [t.definition for t in self.items]] # definition needs the class name to get it from globals and the instance names to get them from the Types

    def _write(self, vals):
        temp = bit()
        for t, v in zip(self.items, vals):
            temp += t.write_bits(v)
        return temp

    def _read(self, bits):
        return [t.read_bits(bits) for t in self.items]

#                                          Dict

class dict_T(static_encoded_type):
    DEFINED = []
    __name__ = 'dict_T_'
    def __init__(self, _items):
        self.items = {key: val for key, val in _items}
        super().__init__(sum([t.bits for t in self.items.values()]))

#                                          List

class list_T(static_encoded_type):
    # note that the _T types should contain n amount of a single static type or a n times repeating set of static types import is they all have to be static so its total length can be known
    DEFINED = []
    __name__ = 'list_T'
    def __init__(self, _items):
        self.items = [item for item in _items]
        super().__init__(sum([t.bits for t in self.items]))
        add_define(list_T, self.definition[1])
        self.name = self.__name__ + f'{len(self.items)}_' if len(self.items) != 1 else '_'
        self.name += str(self.bits)

    @property
    def definition(self):
        return [type(self).__name__, [t.definition for t in self.items]]

    def _write(self, vals:list):
        temp = bit()
        for t, i in zip(self.items, vals):
            temp += t.write_bits(i)
        return temp

    def _read(self, bits):
        return [t.read_bits(bits) for t in self.items]

#                                          Obj

class bit_object(object):
    __slots__ = 'name', '_T', '_type', 'bits'
    def __init__(self, _type, _T, bits):
        self.name = _type.__name__
        self._T = _type
        self._type = _T
        self.bits = bits

    def read_bits(self, bits):
        pass

    def write_bits(self, value):
        pass
