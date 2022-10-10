from opinions.common import ValidationError

from math import floor
import time


class ParserState(object):
    """
    State object for the NMEA parser.
    Rudimentary internal state machine keeps track of where in the parsing process we are
    State 0: Receiving Talker ID (2 chars, in [BD,GA,GB,GL,GN,GP])
    State 1: Receiving sentence type (3 chars)
    State 2: Receiving sentence segments (up to 90 chars, comma-separated)
    State 3: Receiving checksum
    State 4: Ready to pass to sentence parser
    """
    s_state: int = 0
    s_talker: str = ''
    s_type: str = ''
    s_segments: list[str] = []
    s_checksum: str = ''

    @property
    def talker(self):
        return self.s_talker

    @talker.setter
    def talker(self, in_c):
        self.s_talker += in_c
        if len(self.s_talker) == 2:
            self.s_state = 1

    @property
    def type(self):
        return self.s_type

    @type.setter
    def type(self, in_c):
        self.s_type += in_c
        if len(self.s_type) == 3:
            self.s_state = 2

    @property
    def segments(self):
        return ','.join(self.s_segments)

    @segments.setter
    def segments(self, in_c):
        if in_c == ',':
            self.s_segments.append('')
        elif in_c == '*':
            self.s_state = 3
            return
        else:
            self.s_segments[-1] += in_c
        if len(','.join(self.s_segments)) > 90:
            raise ValidationError("Sentence length exceeded 90 characters, there may be a fault")

    @property
    def checksum(self):
        return False

    @checksum.setter
    def checksum(self, in_c):
        self.s_checksum += in_c
        if len(self.s_checksum) == 2:
            self.s_state = 4

    @property
    def next_chr(self):
        return

    @next_chr.setter
    def next_chr(self, in_c):
        if self.s_state == 0:
            self.talker = in_c
            return
        if self.s_state == 1:
            self.type = in_c
            return
        if self.s_state == 2:
            self.segments = in_c
            return
        if self.s_state == 3:
            self.checksum = in_c
            return


class NMEAParser:
    p_state: ParserState = None
    t_offset: int = 0

    def __init__(self, time_offset: int = 0):
        self.p_state = ParserState()
        self.t_offset = time_offset

    def update(self, in_c):
        if type(in_c) is bytes:
            in_c = ord(in_c)
        if type(in_c) is int:
            in_c = chr(in_c)

        if not 20 <= ord(in_c) <= 126 or ord(in_c) not in (10, 13):
            raise ValidationError(f"input character '{in_c}' (ord {ord(in_c)}) not in accepted charset")

        if in_c == '$':
            self.p_state = ParserState()
            return False

        self.p_state.next_chr = in_c

        if self.p_state.s_state == 4:
            return

