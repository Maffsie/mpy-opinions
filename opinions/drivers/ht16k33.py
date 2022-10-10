from time import sleep_ms

from i2cp import I2CPeripheral
from micropython import const


class HT16K33AlNum(I2CPeripheral):
    """
    MicroPython port of the Arduino library for the
    SparkFun Alphanumeric Display
    """

    sym: Dict[int] = {
        ":": 0x01,
        ".": 0x03,
    }
    blinkrate: Dict[int] = {
        0: const(0b00),
        0.5: const(0b11),
        1: const(0b10),
        2: const(0b01),
    }
    cmd: Dict[int] = {
        "dim": const(0b11100000),
        "display": const(0b10000000),
        "system": const(0b00100000),
    }
    state: Dict[int] = {
        "on": const(0b1),
        "off": const(0b0),
    }
    charset: Dict[int] = {
        " ": const(0b00000000000000),
        "!": const(0b00001000001000),
        '"': const(0b00001000000010),
        "#": const(0b01001101001110),
        "$": const(0b01001101101101),
        "%": const(0b10010000100100),
        "&": const(0b00110011011001),
        "'": const(0b00001000000000),
        "(": const(0b00000000111001),
        ")": const(0b00000000001111),
        "*": const(0b11111010000000),
        "+": const(0b01001101000000),
        ",": const(0b10000000000000),
        "-": const(0b00000101000000),
        "/": const(0b10010000000000),
        "0": const(0b00000000111111),
        "1": const(0b00010000000110),
        "2": const(0b00000101011011),
        "3": const(0b00000101001111),
        "4": const(0b00000101100110),
        "5": const(0b00000101101101),
        "6": const(0b00000101111101),
        "7": const(0b01010000000001),
        "8": const(0b00000101111111),
        "9": const(0b00000101100111),
        ";": const(0b10001000000000),
        "<": const(0b00110000000000),
        "=": const(0b00000101001000),
        ">": const(0b10000010000000),
        "?": const(0b01000100000011),
        "@": const(0b00001100111011),
        "A": const(0b00000101110111),
        "B": const(0b01001100001111),
        "C": const(0b00000000111001),
        "D": const(0b01001000001111),
        "E": const(0b00000101111001),
        "F": const(0b00000101110001),
        "G": const(0b00000100111101),
        "H": const(0b00000101110110),
        "I": const(0b01001000001001),
        "J": const(0b00000000011110),
        "K": const(0b00110001110000),
        "L": const(0b00000000111000),
        "M": const(0b00010010110110),
        "N": const(0b00100010110110),
        "O": const(0b00000000111111),
        "P": const(0b00000101110011),
        "Q": const(0b00100000111111),
        "R": const(0b00100101110011),
        "S": const(0b00000110001101),
        "T": const(0b01001000000001),
        "U": const(0b00000000111110),
        "V": const(0b10010000110000),
        "W": const(0b10100000110110),
        "X": const(0b10110010000000),
        "Y": const(0b01010010000000),
        "Z": const(0b10010000001001),
        "[": const(0b00000000111001),
        "\\": const(0b00100010000000),
        "]": const(0b00000000001111),
        "^": const(0b10100000000000),
        "_": const(0b00000000001000),
        "`": const(0b00000010000000),
        "a": const(0b00000101011111),
        "b": const(0b00100001111000),
        "c": const(0b00000101011000),
        "d": const(0b10000100001110),
        "e": const(0b00000001111001),
        "f": const(0b00000001110001),
        "g": const(0b00000110001111),
        "h": const(0b00000101110100),
        "i": const(0b01000000000000),
        "j": const(0b00000000001110),
        "k": const(0b01111000000000),
        "l": const(0b01001000000000),
        "m": const(0b01000101010100),
        "n": const(0b00100001010000),
        "o": const(0b00000101011100),
        "p": const(0b00010001110001),
        "q": const(0b00100101100011),
        "r": const(0b00000001010000),
        "s": const(0b00000110001101),
        "t": const(0b00000001111000),
        "u": const(0b00000000011100),
        "v": const(0b10000000010000),
        "w": const(0b10100000010100),
        "x": const(0b10110010000000),
        "y": const(0b00001100001110),
        "z": const(0b10010000001001),
        "{": const(0b10000011001001),
        "|": const(0b01001000000000),
        "}": const(0b00110100001001),
        "~": const(0b00000101010010),
        "¦": const(0b11111111111111),
    }

    auto_write: bool = False
    buf: bytearray = bytearray(16)
    default_address: int = const(0x70)
    default_brightness: int = const(15)

    segment_count: int = const(14)

    _blink: int = 0
    _brightness: int = 0
    _powered: int = state["off"]

    def init(self, brightness: int = None, auto_write: bool = False):
        if brightness is not None:
            self.default_brightness = brightness
        self.auto_write = auto_write
        if not self.reset():
            raise Exception("Display not responding to writes!")

    def blank(self, write: bool = False):
        self.buf = bytearray(len(self.buf))
        if self.auto_write or write:
            self.show()

    def char(self, chars: str):
        """
        Takes the given <chars> and fetches the byte patterns for each character.
        Returns a List of byte patterns for each character in <chars>.
        NB: Any unrecognised characters are replaced with a default pattern.
        """
        return [self.charset.get(ch, "¦") for ch in chars]

    def poweron(self):
        """
        Powers on the display's processor and output
        """
        self.powered = True

    def poweroff(self):
        """
        Powers off the display's output and processor
        """
        self.powered = False

    def put(self, data: str, offset: int = 0, write: bool = False, **kwargs):
        if "with_colon" not in kwargs.keys():
            kwargs["with_colon"] = ":" in data
        data = data.replace(":", "")
        if "with_dot" not in kwargs.keys():
            kwargs["with_dot"] = "." in data
        data = data.replace(".", "")

        [self.put_one(data[ofs], ofs + offset) for ofs in range(len(data))]
        if self.auto_write or write:
            self.show(**kwargs)

    def put_one(self, data, offset: int = 0, write: bool = False, **kwargs):
        """
        Writes the <data> for a given <offset> to the display memory.
        """

        def resolve(segment, offset):
            # This feels ugly as sin but I don't know how else to do it
            com = segment
            if segment > 8:
                com -= 7
            elif segment == 8:
                com = 0
            elif segment == 7:
                com = 1

            row = offset
            if segment > 6:
                row += 4

            addr = com << 1
            if row > 7:
                addr += 1
            data = 1 << row
            return addr, data

        if type(data) is str:
            data = self.char(data)[0]
        elif type(data) is list and len(data) == 1:
            data = data[0]
        if type(data) is not int:
            return False
        for segment in range(self.segment_count):
            a, d = resolve(segment, offset)
            if (data >> segment) & 0b1:
                self.buf[a] |= d
            else:
                self.buf[a] &= ~d
        if write:
            self.show(**kwargs)

    def write(self, buf: bytes):
        """
        Writes <buf> to the i2c bus at the set address.
        Returns the number of bytes written if successful.
        Returns False if unsuccessful.
        """
        if not self.is_connected:
            print("not connected")
            return False
        return self._write(buf)

    def reset(self):
        """
        Performs a reset sequence:
        - Powers the display power and processor off
        - Sleeps 100ms
        - Powers it back on
        - Erases the display memory
        - Resets the brightness to the last known value
        - Disables any blink frequency
        - Writes the blanked memory to the display
        """
        self.poweroff()
        sleep_ms(100)
        self.poweron()
        self.blank()
        self.brightness = self.default_brightness
        self.blink = 0
        return self.show()

    def show(self, **kwargs):
        """
        Writes the current display memory to the display.
        Optionally accepts <with_colon> and <with_dot> to enable the appropriate lights.
        """
        if "with_colon" in kwargs.keys():
            self.colon = kwargs["with_colon"]
        if "with_dot" in kwargs.keys():
            self.dot = kwargs["with_dot"]

        _buf = bytearray(len(self.buf) + 1)
        _buf[1:] = self.buf
        _buf[0] = 0x00
        return self.write(_buf)

    @property
    def blink(self):
        return self._blink

    @blink.setter
    def blink(self, hz: int):
        """
        Takes the given <hz> and sets the blink rate to it.
        If a blink rate is not supported, the default is 1 Hz.
        If no <hz> is specified, blinking is disabled.
        """
        hz = self.blinkrate.get(hz, 1)
        self._blink = hz
        return self.write(self.cmd["display"] | hz << 1 | self.powered)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, level: int):
        """
        Sets the brightness to the given <level>.
        If the <level> isn't specified, it simply re-sets the brightness
        to the last set brightness (default 15, or 100%)
        """
        self._brightness = level
        return self.write(self.cmd["dim"] | self._brightness)

    @property
    def colon(self):
        return self.buf[self.sym[":"]] & self.state["on"] == 1

    @colon.setter
    def colon(self, state: bool):
        if state:
            self.buf[self.sym[":"]] |= self.state["on"]
        else:
            self.buf[self.sym[":"]] &= ~self.state["on"]
        if self.auto_write or type(state) is int:
            self.show()

    @property
    def dot(self):
        return self.buf[self.sym["."]] & self.state["on"] == 1

    @dot.setter
    def dot(self, state: bool):
        if state:
            self.buf[self.sym["."]] |= self.state["on"]
        else:
            self.buf[self.sym["."]] &= ~self.state["on"]
        if self.auto_write or type(state) is int:
            self.show()

    @property
    def is_connected(self):
        """
        Writes zero bytes to the set address.
        Returns true if a device at the set address ACKs the write.
        Returns false if, after five tries, no ACK is recieved.
        """
        for _ in range(0, 5):
            r = self._write([])
            if type(r) is int and r == 0:
                return True
            sleep_ms(100)
        return False

    @property
    def powered(self):
        return self._powered == self.state["on"]

    @powered.setter
    def powered(self, state: bool):
        """
        Writes the given power <state> to the display's processor and power output registers.
        """
        state = self.state["on"] if state else self.state["off"]
        self.write(self.cmd["system"] | state)
        self.write(self.cmd["display"] | state)
        self._powered = state
