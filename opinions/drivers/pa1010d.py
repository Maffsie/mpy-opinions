from time import sleep_ms
from micropython import const
import _thread

from i2cp import I2CPeripheral
from nmea import NMEAParser

class PA1010D(I2CPeripheral):
    default_address: int = const(0x10)
    run_update_loop: bool = False
    
    def init(self):
        self.lock = _thread.allocate_lock()
        self.nmea = NMEAParser()
    
    def update_loop(self):
        with self.lock:
            if self.run_update_loop: return False
        return _thread.start_new_thread(self.update, ())
    
    def update(self):
        with self.lock:
            self.run_update_loop = True
        while True:
            self.lock.acquire()
            self.nmea.update(self.next_byte)
            if not self.run_update_loop:
                self.lock.release()
                break
            self.lock.release()
            sleep_ms(10)

    @property
    def next_byte(self):
        return self._readfrom(0)

        
