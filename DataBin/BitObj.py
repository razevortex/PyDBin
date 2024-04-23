from bitarray import bitarray as ba # much thanks to ilanschnell
from bitarray.util import int2ba, ba2int

class bit(ba):
    @classmethod
    def readf(cls, file):
        temp = cls()
        with open(file, 'rb') as f:
            temp.fromfile(f)
        return temp[8:-temp[:8].count(1)]

    def cut(self, bits:int):
        temp, self[:] = self[:bits], self[bits:]
        return temp

    def _pad(self):
        i = 0
        pad = [[0 for _ in range(8)], []]
        while (len(self) + i) % 8 != 0:
            pad[0][i] = 1
            pad[1].append(0)
            i += 1
        return bit(pad[0]) + self + bit(pad[1])

    def writef(self, file):
        temp = self if len(self) % 8 == 0 else self._pad()
        with open(file, 'wb') as f:
            temp.tofile(f)

    def rng_array(self, size:int, chance:tuple):
        self.size = size
        return bit([int(rng(0, chance[1]) > chance[0]) for i in range(size)])


def i2b(val:int, len:int, bit_class=bit):
    return bit_class(int2ba(val, len))


def b2i(bits:bit):
    return ba2int(bits)
