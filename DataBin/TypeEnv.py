### somewhat important note befor calling any of these classes here dynamic and static types 
from BitObj import *

class DynamicTypes(object):
    __slots__ = ('bit_int', 'bit_str', 'bit_bool', 'bit_none', 'bit_float', 'bit_list', 'bit_tuple', 'bit_dict')
    def __init__(self):
        [self.__setattr__(slot, globals()[slot]) for slot in self.__slots__]

    @property
    def bits(self):
        return 8

    @property
    def _iterative(self):
        return [self.__getattribute__(slot)() for slot in self.__slots__]

    def write_bits(self, value):
        for i, _t in enumerate(self._iterative):
            if _t == value:
                return i2b(i, self.bits) + _t.write_bits(value)
        return bit()

    def read_bits(self, bits):
        i = b2i(bits.cut(self.bits))
        return self._iterative[i].read_bits(bits)


class StaticTypes(object):
    __slots__ = ('sint', 'uint', 'sfloat', 'sstr', 'tuple_T', 'list_T', 'dict_T') #, 'keywords', 'T_list_n', 'T_tuple_n', 'T_dict_n')
    def __init__(self, *args):
        [self.__setattr__(slot, globals()[slot]) for slot in self.__slots__]
        for arg in args:
            self.__getattribute__(arg[0])(arg[1])

    # This Part is for storeing/loading the defined types to and from files
    @property
    def header(self):
        temp = DynamicTypes().write_bits(self.definition)
        return DynamicTypes().write_bits(len(temp)) + temp

    @classmethod
    def from_file(cls, file):
        length = DynamicTypes().read_bits(file)
        return cls(*DynamicType.read_bits(file.cut(length)))

    @property
    def definition(self):
        return [item.definition for item in self.type_list]

    def build_definition(self, k, v):
        return self.__getattribute__(k)(v)

    # This Part is for the actual read/write of the types values
    @property
    def type_list(self):
        temp = []
        slots = [self.__getattribute__(slot) for slot in self.__slots__]
        for slot in slots:
            for define in slot.DEFINED:
                if not (str(slot.__name__).startswith('tuple') or str(slot.__name__).startswith('list') or str(slot.__name__).startswith('dict')):
                    temp.append(slot(define))
                else:
                    temp.append(slot([self.build_definition(k, v) for k, v in define]))
        return temp

    @property
    def _iterative(self):
        return [t for t in self.type_list]

    @property
    def bits(self):
        return len(self._iterative)

    def get_type(self, key):
        for item in self._iterative:
            if item.name == key:
                return item

class Objects(object):
    __slots__ = 'objects'
    def __init__(self, *args):
        self.objects = [self.add_obj(globals()[arg]) for arg in args]

    @property
    def definition(self):
        return [obj.name for obj in self.objects]

    @property
    def header(self):
        temp = DynamicTypes().write_bits(self.definition)
        return DynamicTypes().write_bits(len(temp)) + temp

    def __len__(self):
        return len(self.objects)

    @classmethod
    def from_file(cls, file):
        length = DynamicTypes().read_bits(file)
        return cls(*DynamicType.read_bits(file.cut(length)))

    def add_obj(self, obj):
        self.objects.append(obj())

    @property
    def _iterative(self):
        return [obj for obj in self.objects]

    @property
    def bits(self):
        return len(self.objects)

class Env(object):
    def __init__(self, name, file=None):
        self.name = name
        self.dynamic = DynamicTypes()
        if not file is None:
            self.static = StaticTypes.from_file(file)
            self.objects = Objects.from_file(file)
        else:
            self.static = StaticTypes()
            self.objects = Objects()
        self.buffer = []

    def add_buffer(self, type_, item):
        self.buffer += [(type_, item)] # type_ = the type class name attribute that should be used to handle it; item = the actual object that should be stored

    @property
    def _iterative(self):
        return self.dynamic._iterative + self.static._iterative + self.objects._iterative

    @property
    def bits(self):
        i = 0
        while 2 ** i <= self.dynamic.bits + self.static.bits + len(self.objects):
            i += 1
        return i

    def declare_static(self, type_:str, definition):
        self.static.__getattribute__(type_)(definition)

    def declare_object(self, type_:type):
        self.objects.add_obj(type_)

    def __repr__(self):
        msg = f'Env {self.name}:\n'
        for i, t in enumerate(self._iterative):
            msg += f'{i}. {t.name}\n'
        return msg

    @property
    def listing(self):
        return [t for t in self._iterative]

    def get_type(self, key):
        for t in self.listing:
            if t.name == key:
                return t

    def write(self):
        temp = bit()
        for _t, item in self.buffer:
            for i, T in enumerate(self.listing):
                if T.name == _t:
                    temp += i2b(i, self.bits)
                    temp += T.write_bits(item)
        return temp

    def read(self, bits):
        arr = []
        while len(bits) > 1:
            temp = self.listing[b2i(bits.cut(self.bits))]
            arr.append(temp.read_bits(bits))
        return arr

    @property
    def body(self):
        temp = bit()
        for _t, item in self.buffer:
            for T in self._iterative:
                if T.name == _t:
                    temp += T.write_bits(item)
        return self.dynamic.write_bits(len(temp)) + temp

