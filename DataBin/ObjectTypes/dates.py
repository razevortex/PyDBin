from DataBin.Types import *
from datetime import datetime as dt, timedelta as td

dateform = '%d.%m.%Y'
timeform = '%H:%M:%S'
datetimeform = dateform + ' ' + timeform

class bit_date(bit_object):
    __slots__ = 'form'
    def __init__(self):
        self.form = dateform
        super().__init__(dt, bit_fchar(), 40)

    def read_bits(self, bits):
        temp = ''.join([self._type.read_bits(bits) for i in range(self.bits // self._type.bits)])
        return dt.strptime(temp, self.form).date()

    def write_bits(self, value):
        temp = bit()
        for char in value.strftime(self.form):
            temp += self._type.write_bits(char)
        return temp

class bit_time(bit_object):
    __slots__ = 'form'
    def __init__(self):
        self.form = timeform
        super().__init__(dt, bit_fchar(), 32)

    def read_bits(self, bits):
        temp = ''.join([self._type.read_bits(bits) for i in range(self.bits // self._type.bits)])
        return dt.strptime(temp, self.form).time()

    def write_bits(self, value):
        temp = bit()
        for char in value.strftime(self.form):
            temp += self._type.write_bits(char)
        return temp

class bit_datetime(bit_object):
    __slots__ = 'form'
    def __init__(self):
        self.form = datetimeform
        super().__init__(dt, bit_fchar(), 76)

    def read_bits(self, bits):
        temp = ''.join([self._type.read_bits(bits) for i in range(self.bits // self._type.bits)])
        return dt.strptime(temp, self.form)

    def write_bits(self, value):
        temp = bit()
        for char in value.strftime(self.form):
            temp += self._type.write_bits(char)
        return temp
