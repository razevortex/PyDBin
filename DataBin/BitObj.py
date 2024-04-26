from bitarray import bitarray as ba # much thanks to ilanschnell
from bitarray.util import int2ba, ba2int

class bit(ba):
    @classmethod
    def readf(cls, file):
        if os.path.exists(file):
            temp = cls()
            with open(file, 'rb') as f:
                temp.fromfile(f)
            return temp[8:-temp[:8].count(1)]
        else:
            return cls()

    def __str__(self):
        i = 0
        temp = ''
        while i < len(self):
            temp += '[' + ''.join([str(t) for t in self[i:i+8]]) + '] '
            i += 8
        return temp

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

    def rng_array(self,  size:int, chance:tuple):
        self.size = size
        return bit([int(rng(0, chance[1]) > chance[0]) for i in range(size)])


def i2b(val:int, len:int):
    return bit(int2ba(val, len))

def b2i(bits:bit):
    return ba2int(bits)

class ProgressivBitWriter(list):
    def __init__(self, file):
        self.filepath = Path(DEFAULT_PATH, file)
        if len(bit.readf(self.filepath)) >= 1:
            super().__init__([bit.readf(self.filepath)])
        else:
            super().__init__([])

    @property
    def get_joined(self):
        temp = bit()
        for b in self:
            temp += b
        return temp

    def fw(self):
        temp = bit()
        for b in self:
            temp += b
        temp.writef(self.filepath)

    def __len__(self):
        return sum([len(item) for item in self])

    def fr(self):
        return bit.readf(self.filepath)

    def __repr__(self):
        return '\n'.join([str(item) for item in self])

    def add(self, bits:bit):
        self.append(bits)
        self.fw()
