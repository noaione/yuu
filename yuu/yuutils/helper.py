import time
from urllib import parse as urlparse

def stringToByteArray(string: str) -> list:
    """
    A port of javascript string to Bytearray function

    :param string: a string
    """
    result = []
    i = 0
    print(len(string))
    while i < len(string):
        a = ord(string[i])
        result.append((65280 & a) >> 8)
        result.append(255 & a)
        i += 1
    return result


def ValueOfDate() -> int:
    """
    Return current unix time in milisecond (Rounded to nearest number)
    """
    return round(time.time() * 1000)


def convertToInt32(_bytes: list) -> list:
    """
    Convert a list of Uint8 to Int32
    Ported from javascript

    :param _bytes: a bytearray
    """
    result = []
    i = 0
    while i < len(_bytes):
        result.append(_bytes[i] << 24 | _bytes[i + 1] << 16 | _bytes[i + 2] << 8 | _bytes[i + 3])
        i += 4
    return result


class toHex:
    def __init__(self, _data: list):
        """
        Convert a list of data to hex

        :param _data: a list of data in bytes or normal
        """
        self.data = _data
        self.buffer = "0123456789abcdef"

    def fromBytes(self) -> str:
        """
        Convert a bytearray to normal hex string
        """
        chance = []
        i = 0
        while i < len(self.data):
            v = self.data[i]
            chance.append(self.buffer[(240 & v) >> 4] + self.buffer[15 & v])
            i += 1
        return "".join(chance)

    def toBytes(self) -> list:
        """
        Convert a list to bytearray
        """
        _bytes = []
        i = 0
        while i < len(self.data):
            _bytes.append(int(self.data[i+2:i+4], 16))
            i += 2
        return _bytes


class toUnicode:
    def __init__(self, data: str):
        """
        Convert a string to UTF-8 list

        :param _data: a list of data in bytes or normal
        """
        self.data = data

    def toBytes(self):
        keys = []
        i = 0
        _str = urlparse.quote_plus(self.data)
        while i < len(_str):
            try:
                section = ord(_str[i+1])
            except:
                break
            if 37 == section:
                keys.append(int(_str[i+2:i+4], 16))
                i += 2
            else:
                keys.append(section)
                i += 1
        return keys

    def fromBytes(self):
        UNICODE_SPACES = []
        index = 0

        while index < len(self.data):
            i = self.data[index]
            if i < 128:
                UNICODE_SPACES.append(chr(i))
                index += 1
            else:
                if i > 191 and i < 224:
                    UNICODE_SPACES.append(chr((31 & i) << 6 | 63 & self.data[index + 1]))
                    index += 2
                else:
                    UNICODE_SPACES.append(chr((15 & i) << 12 | (63 & self.data[index + 1]) << 6 | 63 & self.data[index + 2]))
                    index += 3

        return "".join(UNICODE_SPACES)

